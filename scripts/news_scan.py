#!/usr/bin/env python3
"""Equity Atlas: archived, source-linked GLOBAL NEWS DISCOVERY (not verified investment research).

Runs on GitHub Actions. GDELT DOC ArtList headlines are SAMPLED, not exhaustive.
No live CDS prices. No full article republishing. Public data, no API keys.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/news"
UTC = dt.timezone.utc
now = dt.datetime.now(UTC)
def load(name, default):
    path = DATA/name
    if not path.is_file(): return default
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError): return default

def save(name, obj):
    path = DATA/name
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    tmp.replace(path)

def parse_datetime(raw):
    raw = str(raw or "").strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try: return dt.datetime.strptime(raw, fmt).replace(tzinfo=UTC)
        except ValueError: pass
    return None

def headline_tone(title):
    """Crude headline-language tone only; NOT market impact/sentiment from article body."""
    words = set(re.findall(r"[a-z]+", title.lower()))
    upbeat = {"rise","rises","rally","rallies","surge","surges","gain","gains","growth",
              "expand","expands","eases","ease","recovery","recover","improves","improve",
              "beats","beat","upgrade","upgrades","optimism","relief","deal","deals","truce"}
    gloomy = {"fall","falls","slump","slumps","plunge","plunges","weakens","weaken",
              "war","wars","attacks","attack","default","defaults","downgrade","downgrades",
              "tariff","tariffs","sanctions","crisis","recession","inflation","risk","risks",
              "cuts","cut","declines","decline","sells","selloff","drop","drops","loss","losses"}
    raw = len(words & upbeat) - len(words & gloomy)
    return ("positive" if raw > 0 else "negative" if raw < 0 else "neutral"), raw

def fetch_topic(topic, start, end, maxrecords):
    q = topic["query"]
    params = dict(query=q, mode="artlist", format="json", sort="DateDesc",
                  maxrecords=str(maxrecords),
                  startdatetime=start.strftime("%Y%m%d%H%M%S"),
                  enddatetime=end.strftime("%Y%m%d%H%M%S"))
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "EquityAtlasResearch/1.0 (+https://github.com/ashu2526/equity-atlas)", "Accept":"application/json"})
    for attempt in range(2):
        try:
            with urlopen(req, timeout=45) as resp:
                body = resp.read(5_000_000)
            parsed = json.loads(body.decode("utf-8-sig"))
            if not isinstance(parsed, dict): raise ValueError("non-object API response")
            return parsed.get("articles", []), None
        except Exception as exc:
            if attempt: return [], str(exc)[:250]
            time.sleep(8)
    return [], "unknown"

def main():
    cfg = load("config.json", {})
    topics = cfg.get("topics", [])
    if not topics:
        print("No monitored topics configured", file=sys.stderr)
        return 2
    opts=cfg.get("scan", {})
    lookback=max(1,min(40,int(os.getenv("NEWS_LOOKBACK_DAYS") or opts.get("lookbackDays",14))))
    maxrecords=max(10,min(150,int(opts.get("maxRecordsPerTopic",80))))
    delay=max(5.5,float(opts.get("requestIntervalSeconds",6)))
    earliest=now-dt.timedelta(days=lookback)
    kept = load("articles.json", {"schema":1,"articles":[]})
    known={}
    for article in kept.get("articles",[]):
        if isinstance(article,dict) and article.get("id"):
            known[article["id"]]=article
    results={}
    errors={}
    new=0
    cutoff=now-dt.timedelta(days=max(45,int(opts.get("retentionDays",120))))
    for idx,topic in enumerate(topics):
        if idx: time.sleep(delay)
        name=topic["id"]
        found,error=fetch_topic(topic,earliest,now,maxrecords)
        if error:
            errors[name]=error
            print(name, "FAILED",error[:120],flush=True)
            continue
        results[name]={"sampledCount":len(found),"hitLimit":len(found)>=maxrecords}
        added=0
        for item in found:
            if not isinstance(item,dict): continue
            title=html.unescape(re.sub(r"<[^>]*>","",str(item.get("title") or ""))).strip()
            url=str(item.get("url") or "").strip()
            when=parse_datetime(item.get("seendate"))
            if not (title and len(title)>=10 and when and cutoff<=when<=now+dt.timedelta(days=1)):
                continue
            p=urlsplit(url)
            if p.scheme not in ("http","https") or not p.netloc: continue
            record_id=hashlib.sha1(url.encode("utf-8")).hexdigest()[:20]
            if record_id in known:
                prior=known[record_id]
                prior["topics"]=sorted(set(prior.get("topics",[])+[name]))
                continue
            tone,raw=headline_tone(title)
            known[record_id]={"id":record_id,"title":title[:220],"url":url,
                              "domain":str(item.get("domain") or p.netloc).lower()[:100],
                              "sourcecountry":str(item.get("sourcecountry") or "")[:50],
                              "language":str(item.get("language") or "")[:50],
                              "published":when.isoformat().replace("+00:00","Z"),
                              "discovered":now.isoformat().replace("+00:00","Z"),
                              "topics":[name],"headlineTone":tone,"headlineLexicalScore":raw,
                              "evidenceType":"unverified news headline link"}
            new+=1;added+=1
        print(name, "sample",len(found),"new",added,flush=True)
    if len(results)<max(2,len(topics)//4):
        print("Insufficient successful topic queries; refusing to overwrite archive", file=sys.stderr)
        return 1
    articles=[]
    for a in known.values():
        when=parse_datetime(a.get("published"))
        if when and when>=cutoff:
            articles.append(a)
    articles.sort(key=lambda x:x["published"],reverse=True)
    articles=articles[:max(500,int(opts.get("maxArchivedArticles",6000)))]
    prev=load("scans.json", {"schema":1,"scans":[]}).get("scans",[])
    scan_id=now.strftime("%Y%m%dT%H%M%SZ")
    period=now-dt.timedelta(days=14)
    counts={}
    for a in articles:
        when=parse_datetime(a.get("published"))
        if when and when>=period:
            for t in a["topics"]: counts[t]=counts.get(t,0)+1
    scan={"id":scan_id,"asOf":now.isoformat().replace("+00:00","Z"),
          "windowStart":earliest.isoformat().replace("+00:00","Z"),
          "windowEnd":now.isoformat().replace("+00:00","Z"),
          "collectionMethod":"GDELT DOC 2.0 ArtList: limited sample, not full-text verified",
          "queriesTotal":len(topics),"queriesSucceeded":len(results),"queriesFailed":errors,
          "samplesByTopic":results,"newUniqueArticles":new,"retainedArticles":len(articles),
          "counts14d":counts,
          "coverageWarning":"GDELT lists are rate- and result-capped; missing headlines do not mean absence of risk. Headline tone is NOT investment sentiment.",
          "cdsStatus":"Credit-default-swap headlines only; no live named-issuer or sovereign CDS spread observations"}
    prev=[x for x in prev if isinstance(x,dict) and x.get("id")!=scan_id]
    prev.insert(0,scan)
    prev=prev[:max(10,int(opts.get("maxScanSummaries",120)))]
    save("articles.json",{"schema":1,"source":"GDELT DOC 2.0","provider":"https://www.gdeltproject.org/",
                          "updatedAt":scan["asOf"],"retentionDays":int(opts.get("retentionDays",120)),
                          "firstScanAt":kept.get("firstScanAt") or scan["asOf"],
                          "coverage":"Sampled links/headlines; not an exhaustive search, fact-check or sentiment analysis",
                          "articles":articles})
    save("scans.json",{"schema":1,"scans":prev})
    print("Archived",len(articles),"unique headlines;",len(results),"/",len(topics),"topic queries",flush=True)
    return 0
if __name__=="__main__":
    sys.exit(main())
