#!/usr/bin/env python3
"""Build an auditable market-news climate proxy and sector-attention radar from archived RSS articles.

No LLM calls, no investment recommendations, no CDS/asset-price inference.
The news headline score is an attention/language proxy and explicitly NOT a market price sentiment index.
"""
from __future__ import annotations
import collections
import datetime as dt
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data/news"
UTC=dt.timezone.utc
def read(n,d):
    try:return json.loads((D/n).read_text(encoding="utf-8"))
    except (ValueError,OSError):return d
def write(n,x):
    out=D/n; tmp=out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    tmp.replace(out)
def dtparse(x):
    try:return dt.datetime.fromisoformat(str(x).replace("Z","+00:00")).astimezone(UTC)
    except (ValueError,TypeError):return None
def period_articles(articles,end,days=14):
    start=end-dt.timedelta(days=days)
    return [a for a in articles if (t:=dtparse(a.get("published"))) and start<=t<=end]
def calc(items):
    if not items:return {"items":0,"publishers":0,"positive":0,"negative":0,"neutral":0,
                         "languageIndex":None,"label":"Insufficient observations","sourceConcentration":None}
    pub=collections.defaultdict(list);p=n=z=0
    for a in items:
        t=a.get("headlineTone","neutral")
        p+=int(t=="positive");n+=int(t=="negative");z+=int(t not in ("positive","negative"))
        pub[a.get("domain","unknown")].append(1 if t=="positive" else (-1 if t=="negative" else 0))
    # Reduce dominance from one high-output publisher by averaging publisher averages.
    score=round(100*sum(sum(vals)/len(vals) for vals in pub.values())/len(pub),1)
    concentration=round(100*max(map(len,pub.values()))/len(items),1)
    eligible=len(items)>=8 and len(pub)>=3 and concentration<=75
    label=("Mostly positive headline language" if score>17 else
           "Mostly negative headline language" if score<-17 else
           "Mixed headline language") if eligible else "Insufficient observations"
    return {"items":len(items),"publishers":len(pub),"positive":p,"negative":n,"neutral":z,
            "languageIndex":score,"label":label,"sourceConcentration":concentration,
            "coverageSufficient":eligible}
def main():
    a=read("articles.json",{"articles":[]})
    reviews=read("scans.json",{"scans":[]})
    ed=read("editorial.json",{})
    cfg=read("config.json",{})
    now=dtparse(a.get("updatedAt")) or dt.datetime.now(UTC)
    items=period_articles(a.get("articles",[]),now,14)
    base=calc(items)
    # Comparison is intentionally withheld until the system actually ran across both periods.
    first=dtparse(a.get("firstScanAt"))
    previous_complete=bool(first and first<=now-dt.timedelta(days=28) and len(reviews.get("scans",[]))>=14)
    prev=calc(period_articles(a.get("articles",[]),now-dt.timedelta(days=14),14)) if previous_complete else None
    by_topic=[]
    for topic in cfg.get("topics",[]):
        cur=[x for x in items if topic["id"] in x.get("topics",[])]
        sig=calc(cur)
        prior=[x for x in period_articles(a.get("articles",[]),now-dt.timedelta(days=14),14) if topic["id"] in x.get("topics",[])] if previous_complete else []
        older=calc(prior) if previous_complete else None
        delta=None
        if older and older["coverageSufficient"] and sig["coverageSufficient"] and older["items"]>=5:
            delta=round(100*(sig["items"]-older["items"])/older["items"],1)
        by_topic.append(dict(id=topic["id"],title=topic["label"],**sig,attentionDeltaPct=delta,
                             changeInterpretation=("Rising news coverage" if delta is not None and delta>40 else
                                                   "Cooling news coverage" if delta is not None and delta< -35 else
                                                   "Stable news coverage" if delta is not None else "Not yet measurable"),
                             exampleSources=[{"title":x.get("title"),"url":x.get("url"),"date":x.get("published"),"publisher":x.get("domain")} for x in sorted(cur,key=lambda x:x.get("published",""),reverse=True)[:3]]))
    by_topic.sort(key=lambda x:(x["items"],x["publishers"]),reverse=True)
    mapped={x["Theme ID"]:x for x in ed.get("themes",[])}
    for t in by_topic:
        m=mapped.get(t["id"],{})
        t["directSectors"]=m.get("Direct Sectors","")
        t["proxySectors"]=m.get("Second-order / Proxy Sectors","")
        t["hypothesis"]=m.get("Directional Setup","")
        t["potentialUpside"]=m.get("Potential Beneficiaries if Thesis Holds","")
        t["potentialDownside"]=m.get("Vulnerable / Offsets","")
        t["confirmation"]=m.get("Regime Trigger","")
        t["invalidation"]=m.get("Invalidation","")
        t["hypothesisAsOf"]=m.get("As Of")
    risk=[x for x in by_topic if x["id"] in {"credit_cds","geopolitics","trade_policy","elections_policy","inflation_rates","sovereign_credit","mega_credit","tech_credit"}]
    count=collections.Counter(x.get("domain","unknown") for x in items)
    pulse={
      "schema":1,"generatedAt":now.isoformat().replace("+00:00","Z"),
      "model":"RULES_V1_SOURCE_BALANCED_NO_LLM","mode":"observational_headline_proxy",
      "window":{"start":(now-dt.timedelta(days=14)).date().isoformat(),"end":now.date().isoformat(),"days":14},
      "overall":base,"topics":by_topic,"risks":risk,
      "topPublishers":[{"publisher":k,"stories":v} for k,v in count.most_common(12)],
      "feedCoverage":{"reportedScanCount":len(reviews.get("scans",[])),
                      "latestAvailableFeeds":reviews.get("scans",[{}])[0].get("queriesSucceeded",0) if reviews.get("scans") else 0,
                      "latestConfiguredFeeds":reviews.get("scans",[{}])[0].get("queriesTotal",0) if reviews.get("scans") else 0},
      "historicalComparisonReady":previous_complete,
      "historicalComparisonNote":"Two full 14-day monitoring periods needed; old items discovered in a recent RSS feed do not establish prior-day collection coverage.",
      "marketRegime":"Unconfirmed — missing independently verified price/breadth/credit/earnings-revision factors",
      "cdsStatus":"News coverage only; no issuer or sovereign CDS spread data.",
      "disclaimer":"Headline language is a coarse lexical/source-balanced proxy. It is NOT actual market sentiment or a forward return estimate. Theme transmission hypotheses from editorial data are dated and not freshly validated. Do not rank investments from this index."
    }
    history=read("pulse-history.json",{"schema":1,"snapshots":[]})
    snapshots=[s for s in history.get("snapshots",[]) if s.get("generatedAt","")[:10]!=pulse["generatedAt"][:10]]
    snapshots.insert(0,{"generatedAt":pulse["generatedAt"],"model":pulse["model"],"overall":pulse["overall"],
                        "topics":[{"id":x["id"],"items":x["items"],"publishers":x["publishers"],
                                   "languageIndex":x["languageIndex"],"attentionDeltaPct":x["attentionDeltaPct"]} for x in by_topic],
                        "marketRegime":pulse["marketRegime"]})
    write("market-pulse.json",pulse)
    write("pulse-history.json",{"schema":1,"snapshots":snapshots[:180]})
    print("Market news pulse:",base["items"],"headlines,",base["publishers"],"sources. HEADLINE label:",base["label"])
    print("Real market regime status: NOT VERIFIED")
if __name__=="__main__":main()
