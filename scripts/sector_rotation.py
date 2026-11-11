#!/usr/bin/env python3
"""Read-only NSE NIFTY sector index closes -> 3m sector rotation and regime statistics.

Primary: https://nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv
Fallback: public Yahoo Finance chart endpoint for individual *index* price series.
No holding/institutional flow is estimated from price appreciation. Unavailable -> null.
"""
from __future__ import annotations
import concurrent.futures as futures
import csv
import datetime as dt
import io
import json
import math
import os
from pathlib import Path
import time
from urllib.parse import quote
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError, URLError
from http.cookiejar import CookieJar
from zoneinfo import ZoneInfo

DATA=Path(__file__).resolve().parents[1]/"data/market-signals"
UTC=dt.timezone.utc
TODAY=dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()
BASE="https://nsearchives.nseindia.com/content/indices/ind_close_all_"
INDICES={
"NIFTY 50":("Benchmark","^NSEI"),
"NIFTY BANK":("Banking","^NSEBANK"),
"NIFTY AUTO":("Auto","^CNXAUTO"),
"NIFTY IT":("IT","^CNXIT"),
"NIFTY FMCG":("FMCG","^CNXFMCG"),
"NIFTY METAL":("Metals","^CNXMETAL"),
"NIFTY PHARMA":("Pharma","^CNXPHARMA"),
"NIFTY PSU BANK":("PSU Banks","^CNXPSUBANK"),
"NIFTY PRIVATE BANK":("Private Banks","^NIFTYPVTBANK"),
"NIFTY REALTY":("Realty","^CNXREALTY"),
"NIFTY HEALTHCARE INDEX":("Healthcare","^NIFTYHEALTH"),
"NIFTY CONSUMER DURABLES":("Consumer Durables","^NIFTYCONSRDURBL"),
"NIFTY OIL & GAS":("Oil & Gas","^NIFTY_OIL_AND_GAS"),
"NIFTY FINANCIAL SERVICES":("Financial Services","^CNXFINANCE"),
"NIFTY MEDIA":("Media","^CNXMEDIA"),
"NIFTY INFRASTRUCTURE":("Infrastructure","^CNXINFRA"),
"NIFTY ENERGY":("Energy","^CNXENERGY"),
"NIFTY COMMODITIES":("Commodities","^CNXCOMMODITIES"),
"NIFTY MIDSMALL IT & TELECOM":("MidSmall IT & Telecom",None),
"NIFTY MIDSMALL HEALTHCARE":("MidSmall Healthcare",None)
}
def normalize(s):
    return " ".join(s.upper().replace("–","-").replace("&","&").split())
ALIASES={normalize(k):k for k in INDICES}
ALIASES.update({"NIFTY HEALTHCARE": "NIFTY HEALTHCARE INDEX","NIFTY MIDSMALL HEALTHCARE INDEX":"NIFTY MIDSMALL HEALTHCARE",
"NIFTY INFRA":"NIFTY INFRASTRUCTURE","NIFTY OIL AND GAS":"NIFTY OIL & GAS"})
def read(path,default):
    try:return json.loads((DATA/path).read_text(encoding="utf8"))
    except (OSError,ValueError):return default
def write(path,obj):
    DATA.mkdir(parents=True,exist_ok=True)
    tmp=DATA/(path+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    tmp.replace(DATA/path)
def get_url(url,timeout=10):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
       "Accept":"text/csv,application/json,*/*","Referer":"https://www.nseindia.com/all-reports","Accept-Language":"en-US,en;q=0.9"})
    with build_opener(HTTPCookieProcessor(CookieJar())).open(req,timeout=timeout) as res:
        raw=res.read(350_000)
    return raw
def parse_nse(raw):
    decoded=raw.decode("utf-8-sig",errors="replace")
    if "<html" in decoded[:200].lower():return None
    rd=csv.DictReader(io.StringIO(decoded))
    if not rd.fieldnames:return None
    # Archives have been published with differently cased/spaced headings.
    normalized={normalize(x).replace(" ",""):x for x in rd.fieldnames if x}
    idxcol=next((normalized[k] for k in ("INDEXNAME","INDEX") if k in normalized),None)
    closecol=next((normalized[k] for k in ("CLOSINGINDEXVALUE","CLOSE","CLOSINGVALUE") if k in normalized),None)
    if not idxcol or not closecol:return None
    result={}
    for row in rd:
        key=ALIASES.get(normalize((row.get(idxcol) or "").strip()))
        if not key:continue
        try:v=float(str(row.get(closecol,"")).replace(",",""))
        except (ValueError,TypeError):continue
        if math.isfinite(v) and v>0:result[key]=round(v,5)
    return result if len(result)>=5 else None
def fetch_day(d):
    url=BASE+d.strftime("%d%m%Y")+".csv"
    try:
        row=parse_nse(get_url(url,timeout=8))
        return (d.isoformat(),row,None if row else "CSV unavailable/unrecognized")
    except (HTTPError,URLError,TimeoutError) as e:
        return (d.isoformat(),None,str(e)[:80])
    except Exception as e:return(d.isoformat(),None,str(e)[:90])
def yahoo_chart(symbol,start,end):
    if not symbol:return []
    import calendar
    t1=calendar.timegm(dt.datetime.combine(start,dt.time.min,tzinfo=UTC).timetuple())
    t2=calendar.timegm(dt.datetime.combine(end+dt.timedelta(days=1),dt.time.min,tzinfo=UTC).timetuple())
    url="https://query1.finance.yahoo.com/v8/finance/chart/"+quote(symbol,safe="")+"?period1="+str(t1)+"&period2="+str(t2)+"&interval=1d"
    try:
        raw=get_url(url,timeout=15)
        obj=json.loads(raw)
        result=obj["chart"]["result"][0]
        timestamps=result.get("timestamp",[])
        closes=result["indicators"]["quote"][0].get("close",[])
        values=[]
        for ts,v in zip(timestamps,closes):
            if isinstance(v,(int,float)) and math.isfinite(v) and v>0:
                values.append((dt.datetime.fromtimestamp(ts,UTC).date().isoformat(),round(v,5)))
        return values
    except Exception:return []
def calculate(series,now):
    days=sorted(series)
    latest=days[-1] if days else None
    if not latest:return None
    last=series[latest]
    def nearest(target,maxgap=12):
        candidates=[day for day in days if day<=target]
        if not candidates:return None
        d=candidates[-1]
        return series[d] if (dt.date.fromisoformat(target)-dt.date.fromisoformat(d)).days<=maxgap else None
    def value_days_ago(n):
        target=(dt.date.fromisoformat(latest)-dt.timedelta(days=n)).isoformat()
        return nearest(target)
    def r(a,b):
        return round(100*(a/b-1),2) if a and b and b>0 else None
    prev7=value_days_ago(7);prev30=value_days_ago(30);prev60=value_days_ago(60);prev91=value_days_ago(91)
    one=r(last,prev30)
    prev_one=r(prev30,prev60)
    accel=round(one-prev_one,2) if one is not None and prev_one is not None else None
    path=[{"date":d,"close":series[d]} for d in days if d>=(dt.date.fromisoformat(latest)-dt.timedelta(days=100)).isoformat()]
    return {"latestDate":latest,"latestClose":last,"daysObserved":len(days),
        "r7d":r(last,prev7),"r1m":one,"rPrev1m":prev_one,"r3m":r(last,prev91),
        "momentumAccelerationPp":accel,"path":path}
def main():
    old=read("index-history.json",{"daily":{},"yahooSeries":{}})
    daily=old.get("daily",{})
    oldest=TODAY-dt.timedelta(days=119)
    daily={d:v for d,v in daily.items() if d>=oldest.isoformat() and isinstance(v,dict)}
    backfill=not any(k <= (TODAY-dt.timedelta(days=80)).isoformat() for k in daily)
    if backfill:
        dates=[oldest+dt.timedelta(days=i) for i in range(120) if (oldest+dt.timedelta(days=i)).weekday()<5 and (oldest+dt.timedelta(days=i)).isoformat() not in daily]
    else:
        dates=[TODAY-dt.timedelta(days=i) for i in range(8) if (TODAY-dt.timedelta(days=i)).weekday()<5 and (TODAY-dt.timedelta(days=i)).isoformat() not in daily]
    errors={}
    if dates:
        with futures.ThreadPoolExecutor(max_workers=8) as pool:
            for d,row,error in pool.map(fetch_day,dates):
                if row:daily[d]=row
                elif error:errors[d]=error
    daily=dict(sorted(daily.items()))
    histories={key:{} for key in INDICES}
    for day,row in daily.items():
        for k,v in row.items():
            if k in histories and isinstance(v,(int,float)) and v>0:histories[k][day]=v
    # Partial NSE archive / blocked archive: fallback to Yahoo ONLY for indices with no 3m coverage.
    fallbacks={}
    for k,(label,symbol) in INDICES.items():
        series=histories[k]
        enough=(len(series)>=30 and min(series)<= (TODAY-dt.timedelta(days=79)).isoformat())
        if enough:continue
        yahoo=old.get("yahooSeries",{}).get(k,{})
        vals=yahoo_chart(symbol,oldest,TODAY) if symbol else []
        if vals:
            yahoo.update(dict(vals))
            yahoo={d:v for d,v in yahoo.items() if d>=oldest.isoformat()}
            histories[k]=yahoo
            fallbacks[k]={"source":"Yahoo Finance chart mirror","observations":len(yahoo)}
            old.setdefault("yahooSeries",{})[k]=yahoo
    benchmark=calculate(histories["NIFTY 50"],TODAY)
    result=[];missing=[]
    for index,(sector,symbol) in INDICES.items():
        c=calculate(histories[index],TODAY)
        if not c or not c["r3m"] is not None:
            missing.append(index)
            # Still display partial records if present; mark coverage issue.
        if not c:continue
        benchmark3=benchmark["r3m"] if benchmark else None
        benchmark1=benchmark["r1m"] if benchmark else None
        relative=round(c["r3m"]-benchmark3,2) if c["r3m"] is not None and benchmark3 is not None else None
        relative1=round(c["r1m"]-benchmark1,2) if c["r1m"] is not None and benchmark1 is not None else None
        accel=c["momentumAccelerationPp"]
        if c["r3m"] is None:state="Insufficient 3-month history"
        elif relative is not None and relative>0 and relative1 is not None and relative1>0 and accel is not None and accel>0:state="Leading & accelerating"
        elif relative is not None and relative>0 and accel is not None and accel<0:state="Leading, momentum cooling"
        elif relative is not None and relative<0 and accel is not None and accel>0:state="Lagging, early rebound"
        elif relative is not None and relative<0:state="Lagging benchmark"
        else:state="Mixed / no clear trend"
        result.append({"index":index,"sector":sector,"yahooTicker":symbol,
            "priceSource":fallbacks.get(index,{}).get("source","NSE India official daily index snapshot"),
            "sourceUrl":"https://finance.yahoo.com/" if index in fallbacks else
              "https://www.nseindia.com/all-reports",
            "relative3mPp":relative,"relative1mPp":relative1,"rotationState":state,**c})
    ordered=[i for i in result if i["index"]!="NIFTY 50"]
    ordered.sort(key=lambda z:(z["relative3mPp"] is None,-(z["relative3mPp"] or 0)))
    for i,v in enumerate(ordered):v["researchRank"]=i+1 if v["relative3mPp"] is not None else None
    all_latest=max((x["latestDate"] for x in result),default=None)
    recent=(TODAY-dt.date.fromisoformat(all_latest)).days if all_latest else None
    out={
       "schema":1,"generatedAt":dt.datetime.now(UTC).isoformat(),"asOf":all_latest,
       "market":"India (NSE NIFTY sector price-return indices)",
       "status":"ready" if benchmark and benchmark["r3m"] is not None and recent is not None and recent<=6 and len(ordered)>=9 else "partial_or_unavailable",
       "sourcePriority":["NSE official ind_close_all daily reports","Yahoo Finance chart mirror, tagged per-index when used"],
       "benchmarkIndex":"NIFTY 50",
       "benchmark":benchmark and {k:v for k,v in benchmark.items() if k!="path"},
       "benchmarkPath":benchmark.get("path",[]) if benchmark else [],
       "sectors":ordered,
       "missingIndices":missing,
       "sourceDiagnostics":{"nseDailyFiles":len(daily),"nseAttemptedThisRun":len(dates),"nseFailedThisRun":len(errors),
                            "nseErrorExamples":list(errors.items())[:5],"fallbackIndexCount":len(fallbacks),"fallbackIndices":list(fallbacks)},
       "rules":{"returns":"Price returns from comparable historical index closes (dividends excluded), closest at/before 7/30/91 calendar days; lookback missing if >12 days gap",
                "relative3m":"sector 3m return minus NIFTY 50 3m return, percentage points",
                "acceleration":"latest 30 calendar-day price return minus preceding 30 calendar-day price return, percentage points",
                "notCapitalFlow":"Index prices/rankings cannot prove FPI/DII sector purchases or institutional inflows; compare NSDL sector flow figures separately",
                "missingData":"If archive or Yahoo access fails, no returns are invented; show null and source status"}
    }
    write("index-history.json",{"schema":1,"source":"NSE index daily archives plus tagged Yahoo fallbacks",
                               "lastAttemptAt":out["generatedAt"],"daily":daily,"yahooSeries":old.get("yahooSeries",{})})
    write("sector-rotation.json",out)
    print("Sector rotation",out["status"],"latest",all_latest,"NSE daily files",len(daily),"fallback indices",len(fallbacks),
          "complete 3m",sum(x["r3m"] is not None for x in ordered),"of",len(ordered))
if __name__=="__main__":main()
