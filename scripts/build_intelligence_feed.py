#!/usr/bin/env python3
"""Daily market-moving headline prioritization, clustering and attribution from the existing RSS archive.

RULES, not LLM. This produces a transparent evidence feed, not original reporting or AI analysis.
Do not infer actual capital flows or financial market returns from headlines.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import datetime as dt
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data/news"
UTC=dt.timezone.utc

def read(name,default):
    try:return json.loads((D/name).read_text(encoding="utf-8"))
    except (OSError,ValueError):return default
def write(name,obj):
    path=D/name;tmp=path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    tmp.replace(path)
def timeparse(s):
    try:return dt.datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(UTC)
    except (ValueError,AttributeError):return None

STOP=set("the a an with for from and or to of as in on at by its his her their over under after before amid has have had say says says that this those is are was were it how why what about into new us u s india indian world asso said more than".split())
MATERIAL=[(r"\b(?:default|bankruptcy|credit crisis|downgrade|bank failure|liquidity crunch|debt crisis)\b",8),
(r"\b(?:rate hike|rate cut|interest rate|inflation shock|central bank|rbi|fed|federal reserve|cpi)\b",5),
(r"\b(?:tariff|export control|sanction|trade war|customs|import duty)\b",6),
(r"\b(?:war|invasion|attack|missile|ceasefire|hormuz|shipping disruption|oil embargo)\b",7),
(r"\b(?:fpi|fii|foreign funds|capital inflow|investors? pull|institutional flow)\b",6),
(r"\b(?:oil price|brent|crude|opec|natural gas|rubber)\b",4),
(r"\b(?:earnings|profit warning|guidance cut|revenue miss|forecast|capex|investment)\b",4),
(r"\b(?:election|parliament|midterms|president|trade pact|agreement)\b",3),
(r"\b(?:record high|record low|rallies|plunges|bear market|market selloff)\b",3),
(r"\b(?:buyout|takeover|merger|acquisition|deal|stake|ipo)\b",3)]
MR=[(re.compile(p,re.I),v) for p,v in MATERIAL]
COUNTRIES={
"India":r"\b(?:india|indian|nifty|sensex|rbi|rupee|mumbai|new delhi|sebi)\b",
"United States":r"\b(?:us|u\.s\.|united states|washington|federal reserve|wall street|fed |s&p|nasdaq)\b",
"Europe":r"\b(?:europe|european|eu |ecb|germany|france|uk |britain|united kingdom|london)\b",
"China":r"\b(?:china|chinese|beijing|shanghai|hong kong)\b",
"Middle East":r"\b(?:iran|israel|hormuz|gulf|saudi|qatar|uae|middle east)\b",
"Russia / Ukraine":r"\b(?:russia|russian|ukraine|ukrainian)\b",
"Japan":r"\b(?:japan|tokyo|yen|boj)\b"}
CR=[(k,re.compile(p,re.I)) for k,p in COUNTRIES.items()]
TOPIC_ENGINES={
"india_flows":("Cross-border equity allocation","Flows may change the marginal equity buyer and valuation; verify actual transactions and sector attribution, not just index gains.","NSE FII/DII net trades; NSDL sector flows; earnings revisions"),
"inflation_rates":("Discount rate and funding cost","Policy rates and inflation change borrowing costs and the valuation of long-duration cash flows.","Central bank release; yields and credit spreads; inflation surprises"),
"credit_cds":("Credit availability and refinancing","Widening financing costs can precede stress for leveraged sectors; issuer CDS headlines alone do not establish spread levels.","Verified CDS/bond observations, credit ratings and funding maturities"),
"energy_shipping":("Landed energy and freight costs","Fuel, freight and insurance pass through to corporate gross margins with lags.","Brent, actual freight/insurance routes and company gross margins"),
"geopolitics":("Geopolitical disruption and risk premiums","Military events may disrupt commodities, transport, trade or procurement, but second-order effects need corroboration.","Physical disruptions, sanctions implementation, commodity and credit moves"),
"trade_policy":("Tariff and supply-chain transmission","Actual enacted duties can redistribute costs and orders among exporters, importers and domestic substitutes.","Published tariff text; issuer revenue exposure; order book and landed cost"),
"ai_rotation":("Global technology capex economics","AI investment may help suppliers while valuation and monetisation concerns create market dislocations.","Hyperscaler capex guidance, orders, cash returns and analyst revisions"),
"elections_policy":("Policy credibility and fiscal allocation","Election promises matter less than enacted laws, budgets and funding channels.","Official legislation and funding; real orders and currency/rate response"),
"healthcare":("Health capacity productivity","Hospital economics depend on mature occupancy, case mix, payer mix and cash returns to new beds.","Facility EBITDA and occupancy; ARPOB; capex/ROIC"),
"tyre_inputs":("Rubber-price pass-through","Input basket and price-change lags alter tyre manufacturer margins.","Rubber, petroleum-derived inputs, realisation and gross profit"),
"auto_consumer":("Consumer affordability and industry volumes","Pricing, interest rates, dealer inventories and retail sell-through decide auto and downstream margin.","Registration data; OEM/retail volume; inventory and financing rates"),
"defence_capex":("Defence funding and execution","Geopolitical risks matter to listed firms only through funded contracts and realized cash returns.","Defence budgets, contract awards, shipments and receivables"),
"climate_agri":("Crop income and input-price supply","Weather outcomes can affect farm cash flows, food prices, FMCG demand and agricultural equipment.","IMD realised weather, crop output, CPI, rural volumes")
}
DOMAIN_BONUS={"www.reuters.com":2,"www.bloomberg.com":1.5,"www.thehindu.com":1.5,"www.bbc.co.uk":1.1,"www.federalreserve.gov":2,"www.ecb.europa.eu":2}

def words(headline):
    return set(w for w in re.findall(r"[a-z]{3,}",headline.lower()) if w not in STOP)
def overlap(a,b):
    x=words(a);y=words(b)
    return len(x&y)/len(x|y) if x and y else 0
def score(item,now):
    head=item.get("title","")
    val=sum(n for pattern,n in MR if pattern.search(head))
    v=set(item.get("topics",[]))
    if "credit_cds" in v or "sovereign_credit" in v:val+=3
    if "india_flows" in v or "trade_policy" in v:val+=2
    val+=min(3,len(v))
    val+=DOMAIN_BONUS.get(item.get("domain",""),0)
    published=timeparse(item.get("published"))
    hours=max(0,(now-published).total_seconds()/3600) if published else 600
    recency=4 if hours<24 else 3 if hours<48 else 2 if hours<96 else 1 if hours<168 else 0
    return round(val+recency,1)
def main():
    article_source=read("articles.json",{"articles":[]})
    edited=read("editorial.json",{"themes":[]})
    archive=article_source.get("articles",[])
    now=timeparse(article_source.get("updatedAt")) or dt.datetime.now(UTC)
    cutoff=now-dt.timedelta(days=14)
    relevant=[a for a in archive if (t:=timeparse(a.get("published"))) and cutoff<=t<=now and a.get("topics")]
    relevant.sort(key=lambda a:(-score(a,now),a.get("published","")))
    groups=[]
    for a in relevant:
        matched=False
        for g in groups:
            representative=g[0]
            same=bool(set(a.get("topics",[]))&set(representative.get("topics",[])))
            day=abs((timeparse(a["published"])-timeparse(representative["published"])).days)
            if same and day<4 and overlap(a["title"],representative["title"])>=0.53:
                g.append(a);matched=True;break
        if not matched:groups.append([a])
    mapping={t["Theme ID"]:t for t in edited.get("themes",[])}
    cards=[]
    for group in groups:
        group.sort(key=lambda a:score(a,now),reverse=True)
        head=group[0]
        topics=sorted(set(t for a in group for t in a.get("topics",[])))
        main=next((t for t in topics if t in mapping),topics[0])
        meta=mapping.get(main,{})
        engine=TOPIC_ENGINES.get(main,("Unresolved economic pathway","Needs further verification before attributing a tradeable impact.","Source report and market prices"))
        domains={a.get("domain") for a in group if a.get("domain")}
        rank=score(head,now)+min(3,len(domains)-1)
        if rank>=16 and len(domains)>=2:prio="Major — multiple publishers"
        elif rank>=13:prio="High — verify sources"
        elif rank>=9:prio="Medium — monitor"
        else:prio="Context"
        regions=[label for label,r in CR if any(r.search(a.get("title","")) for a in group)] or ["Unspecified / cross-border"]
        cards.append({
         "id":head["id"],"published":head["published"],"priorityScore":round(rank,1),
         "priority":prio,"headline":head["title"],"headlineType":"Unverified publisher RSS headline",
         "whatWeKnow":"Headline reported by "+head.get("domain","unknown publisher")+"; full event details require reading source article.",
         "whyItMatters":engine[1],"transmissionChannel":engine[0],"watchNext":engine[2],
         "topics":topics,"primaryTheme":main,"geographies":regions,
         "directSectors":meta.get("Direct Sectors","Not sector-mapped"),
         "proxySectors":meta.get("Second-order / Proxy Sectors","Not sector-mapped"),
         "possibleBeneficiaries":meta.get("Potential Beneficiaries if Thesis Holds","Unknown"),
         "possibleLosers":meta.get("Vulnerable / Offsets","Unknown"),
         "thesisTest":meta.get("Regime Trigger","Await confirmation"),
         "thesisInvalidation":meta.get("Invalidation","No company evidence"),
         "sourceCount":len(group),"independentDomains":len(domains),
         "sources":[{"title":a["title"],"publisher":a.get("domain"),
                     "url":a["url"],"published":a["published"]} for a in group[:5]],
         "sourceCoverage":"RSS headline snippets only. Multi-domain overlap is not independently verified fulltext.",
         "isVerified":False,"smartMoneyStatus":"No direct flow measurement from this headline"
        })
    cards.sort(key=lambda a:(-a["priorityScore"],a["published"]))
    stories=cards[:80]
    themeCounts=Counter(t for a in relevant for t in a.get("topics",[]))
    geographyCounts=Counter(c for a in relevant for c,r in CR if r.search(a.get("title","")))
    latest={
     "schema":1,"generatedAt":now.isoformat().replace("+00:00","Z"),
     "scope":{"windowStart":cutoff.date().isoformat(),"windowEnd":now.date().isoformat(),"headlineCount":len(relevant),
              "clusterCount":len(groups),"publishedCards":len(stories),"rankingMethod":"transparent keyword-materiality, source diversity and recency; not AI"},
     "topThemeCounts":[{"theme":k,"headlines":v} for k,v in themeCounts.most_common()],
     "geographyMentions":[{"geography":k,"headlines":v,"warning":"NEWS MENTIONS, not fund flows"} for k,v in geographyCounts.most_common()],
     "cards":stories,
     "limitDisclosure":"RSS sample is incomplete. Ranking is a heuristic triage score, not event importance independently validated by an editor. A country mentioned in news is not where money moved."
    }
    write("ranked-feed.json",latest)
    older=read("ranked-feed-history.json",{"schema":1,"snapshots":[]})
    snaps=[s for s in older.get("snapshots",[]) if s.get("asOf")!=now.date().isoformat()]
    snaps.insert(0,{"asOf":now.date().isoformat(),"headlines":len(relevant),
                    "clusters":len(groups),"topicCounts":dict(themeCounts),"geoMentions":dict(geographyCounts)})
    write("ranked-feed-history.json",{"schema":1,"snapshots":snaps[:365]})
    print("Ranked",len(stories),"top clusters from",len(relevant),"headlines,",
          len(domains) if groups else 0,"domains in last selected cluster; labels NOT AI")

if __name__=="__main__":main()
