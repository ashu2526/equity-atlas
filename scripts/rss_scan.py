#!/usr/bin/env python3
"""Equity Atlas RSS news-link discovery and regime archive. Public headlines, no full text, no API keys.

Not exhaustive. Never infer market or company CDS prices from RSS. Fail closed if feeds unavailable.
"""
from __future__ import annotations
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/news"
UTC=dt.timezone.utc
NOW=dt.datetime.now(UTC)

def load(name,default):
    try: return json.loads((DATA/name).read_text(encoding="utf-8"))
    except (ValueError,OSError): return default
def save(name,obj):
    dest=DATA/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_suffix(dest.suffix+".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(dest)
def parse_date(v):
    if not v: return None
    try:
        result=email.utils.parsedate_to_datetime(str(v))
        if result.tzinfo is None: result=result.replace(tzinfo=UTC)
        return result.astimezone(UTC)
    except Exception: pass
    value=str(v).strip()
    try:
        result=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
        if result.tzinfo is None:result=result.replace(tzinfo=UTC)
        return result.astimezone(UTC)
    except Exception:return None
def field(item,name):
    for el in item:
        if el.tag.rsplit("}",1)[-1].lower()==name.lower():
            return (el.text or "").strip()
    return ""
def parsed_items(raw):
    root=ET.fromstring(raw)
    for item in root.iter():
        if item.tag.rsplit("}",1)[-1] not in ("item","entry"):continue
        title=html.unescape(re.sub(r"<[^>]+>","",field(item,"title"))).strip()
        link=field(item,"link")
        if not link:
            for el in item:
                if el.tag.rsplit("}",1)[-1]=="link":
                    link=el.attrib.get("href","").strip()
                    if link:break
        when=parse_date(field(item,"pubDate") or field(item,"published") or field(item,"updated") or field(item,"date"))
        if not (title and link and when):continue
        yield title,link,when
def headline_tone(title):
    words=set(re.findall(r"[a-z]+",title.lower()))
    good={"rally","rallies","recovery","recovers","grow","growth","upgrades","upgrade","rise","rises","jump","jumps","improve","improves","eases","easing","deal","deals","truce","record","boost","gain","gains"}
    bad={"war","wars","crisis","attack","attacks","downgrade","downgrades","default","defaults","inflation","tariffs","tariff","sanctions","slump","slumps","plunge","plunges","fall","falls","drop","drops","cuts","cut","weakens","weak","decline","declines","tensions","disruptions","risk","risks"}
    value=len(words & good)-len(words & bad)
    return ("positive" if value>0 else "negative" if value<0 else "neutral"),value

TOPIC_MATCH={
"india_flows":r"\b(?:fpi|fii|foreign investors|foreign funds|nifty|sensex|rupee|indian stocks|india equities|investor inflows)\b",
"energy_shipping":r"\b(?:oil prices?|brent|crude|tanker|hormuz|maritime|freight|shipping|petroleum|lng|opec)\b",
"inflation_rates":r"\b(?:inflation|fed|federal reserve|rbi|repo rate|interest rates?|bond yields?|monetary policy|ecb|central banks?|cpi)\b",
"ai_rotation":r"\b(?:artificial intelligence|ai capex|ai spending|nvidia|openai|anthropic|data cent(?:er|re)|gpu|semiconductor|chipmakers?|machine learning)\b",
"trade_policy":r"\b(?:tariffs?|trade war|export controls?|trade deal|customs duties|embargo|import duties|sanctions)\b",
"geopolitics":r"\b(?:ukraine|russia|iran|israel|gaza|strait of hormuz|war|military attacks|missiles?|ceasefire|peace talks|sanctions)\b",
"credit_cds":r"\b(?:cds|credit default swaps?|credit spreads?|sovereign debt|debt crisis|credit downgrade|bond defaults?|debt default)\b",
"elections_policy":r"\b(?:elections?|votes?|voting|parliament|congress|senate|midterm|political parties|coalition|new government|legislation)\b",
"auto_consumer":r"\b(?:automakers?|auto sales|automotive|passenger vehicles?|car sales|two[- ]wheelers?|tractor sales|consumer spending|retail sales)\b",
"healthcare":r"\b(?:hospitals?|healthcare|medical insurance|drugmakers?|pharmaceuticals?|health services|medtech)\b",
"tyre_inputs":r"\b(?:tyres?|tires?|rubber prices?|natural rubber|carbon black|balkrishna industries|mrf|ceat)\b",
"defence_capex":r"\b(?:defen[cs]e|arms deal|military spending|weapons?|defence orders?|aircraft carriers?|security spending)\b",
"climate_agri":r"\b(?:monsoon|el ni[nñ]o|floods?|drought|food prices?|crop yields?|agriculture|farm income|rainfall)\b",
"mega_credit":r"\b(?:jpmorgan|goldman sachs|deutsche bank|citigroup|hsbc|hdfc bank|icici bank|state bank of india|sbi)\b",
"sovereign_credit":r"\b(?:sovereign debt|bond yields?|credit ratings?|national debt|fiscal deficit|debt ceiling|treasury yields?)\b",
"tech_credit":r"\b(?:data cent(?:er|re) financing|ai financing|big tech debt|tech credit|hyperscaler|nvidia|alphabet|microsoft|amazon)\b"
}
REGEX={key:re.compile(value,re.I) for key,value in TOPIC_MATCH.items()}
def topics(title):
    return sorted(key for key,regex in REGEX.items() if regex.search(title))
def feed_get(feed):
    req=urllib.request.Request(feed["url"],headers={
        "User-Agent":"EquityAtlasPersonalNewsReader/1.0 (contact: GitHub repo ashu2526/equity-atlas)",
        "Accept":"application/rss+xml, application/atom+xml, application/xml, text/xml",
    })
    with urllib.request.urlopen(req,timeout=14) as response:
        return list(parsed_items(response.read(2_000_000)))

def main():
    cfg=load("config.json",{})
    feeds=cfg.get("feeds",[])
    opts=cfg.get("scan",{})
    if not feeds:raise SystemExit("No RSS feeds configured")
    old=load("articles.json",{"articles":[]})
    records={a["id"]:a for a in old.get("articles",[]) if a.get("id")}
    cutoff=NOW-dt.timedelta(days=int(opts.get("retentionDays",120)))
    max_items=int(opts.get("maxFeedItems",100))
    errors={}
    successes={}
    new=0
    new_by_topic={}
    for f in feeds:
        name=f["name"]
        try:
            items=feed_get(f)
            successes[name]=len(items)
        except Exception as exc:
            errors[name]=str(exc)[:160]
            print(name,"feed failed:",errors[name],flush=True)
            continue
        added=0
        for title,url,when in items[:max_items]:
            if when<cutoff or when>NOW+dt.timedelta(days=1):continue
            parsed=urlsplit(url)
            if parsed.scheme not in ("https","http") or not parsed.netloc:continue
            labels=topics(title)
            if not labels:continue
            record_id=hashlib.sha1(url.encode("utf8")).hexdigest()[:20]
            if record_id in records:
                a=records[record_id]
                a["topics"]=sorted(set(a.get("topics",[])+labels))
                a["feedSources"]=sorted(set(a.get("feedSources",[])+[name]))
                continue
            tone,lexical=headline_tone(title)
            records[record_id]={
                "id":record_id,"title":title[:220],"url":url,"domain":parsed.netloc.lower(),
                "sourcecountry":"","language":"English","published":when.isoformat().replace("+00:00","Z"),
                "discovered":NOW.isoformat().replace("+00:00","Z"),"topics":labels,
                "feedSources":[name],"headlineTone":tone,"headlineLexicalScore":lexical,
                "evidenceType":"publisher RSS headline/link — source not full-text verified"
            }
            added+=1;new+=1
            for tag in labels:new_by_topic[tag]=new_by_topic.get(tag,0)+1
        print(name,"items",len(items),"new tagged",added,flush=True)
        time.sleep(.2)
    if len(successes)<3:
        print("Only",len(successes),"feeds accessible; refusing false update",file=sys.stderr)
        return 1
    all_articles=[a for a in records.values() if (d:=parse_date(a.get("published"))) and d>=cutoff]
    all_articles.sort(key=lambda x:x["published"],reverse=True)
    all_articles=all_articles[:int(opts.get("maxArchivedArticles",6000))]
    prev=load("scans.json",{"scans":[]}).get("scans",[])
    scan_id=NOW.strftime("%Y%m%dT%H%M%SZ")
    p14=NOW-dt.timedelta(days=14)
    counts={}
    for a in all_articles:
        if parse_date(a.get("published"))>=p14:
            for topic in a.get("topics",[]):counts[topic]=counts.get(topic,0)+1
    coverage_start=min((a["published"] for a in all_articles),default=None)
    scan={
        "id":scan_id,"asOf":NOW.isoformat().replace("+00:00","Z"),
        "collectionMethod":"Publisher + official RSS feeds; headline title/link only",
        "sourceFeedsConfigured":len(feeds),"queriesTotal":len(feeds),"queriesSucceeded":len(successes),
        "queriesFailed":errors,"feedItemsSeen":successes,"newUniqueArticles":new,
        "retainedArticles":len(all_articles),"counts14d":counts,"newByTopic":new_by_topic,"oldestRetainedAt":coverage_start,
        "lookbackDays":int(opts.get("lookbackDays",14)),
        "coverageWarning":"Selected publisher feeds only; RSS feeds vary in update frequency and length, no exhaustive news or CDS price data.",
        "cdsStatus":"CDS-related press headlines; no verified live named-issuer CDS spreads"
    }
    prev=[s for s in prev if s.get("id")!=scan_id]
    prev.insert(0,scan)
    prev=prev[:int(opts.get("maxScanSummaries",120))]
    save("articles.json",{
        "schema":1,"source":"Publisher and institutional RSS feeds","updatedAt":scan["asOf"],
        "retentionDays":int(opts.get("retentionDays",120)),
        "firstScanAt":old.get("firstScanAt") or scan["asOf"],
        "firstCoveredAt":old.get("firstScanAt") or scan["asOf"],
        "coverage":"Selected source feeds and headline keyword matching only. Some publisher feeds may fail, truncate, or be stale.",
        "articles":all_articles
    })
    save("scans.json",{"schema":1,"scans":prev})
    print("Archived",len(all_articles),"tagged articles; sources",len(successes),"/",len(feeds),"new",new,flush=True)
    return 0

if __name__=="__main__":sys.exit(main())
