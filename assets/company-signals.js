/* Stock Price × Volume UI: source-first, no front-end quote fetching or dependencies. */
(()=>{"use strict";
const $=s=>document.querySelector(s);
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt=v=>v==null||!Number.isFinite(Number(v))?"—":Number(v).toLocaleString("en-IN",{maximumFractionDigits:2});
const sign=v=>v==null?"—":(v>0?"+":"")+Number(v).toFixed(2)+"%";
let state={stocks:[],selected:"YATHARTH",days:120};
const good=x=>x.dataStatus==="ready";
function universe(){
 const stocks=state.stocks;
 const sectors=[...new Set(stocks.map(x=>x.sector).filter(Boolean))].sort();
 $("#industry").innerHTML='<option value="">All industries</option>'+sectors.map(x=>'<option>'+esc(x)+'</option>').join("");
 const ready=stocks.filter(good),signals=ready.filter(x=>x.signals?.length);
 $("#headlineMetrics").innerHTML=[
 ["Tracked companies",stocks.length],["Current data",ready.length+"/"+stocks.length],
 ["Flagged patterns",signals.length],["High-priority",ready.filter(x=>x.signals?.some(y=>y.priority==="high")).length]
 ].map(x=>'<div class="pv-metric"><small>'+esc(x[0])+'</small><b>'+esc(x[1])+'</b></div>').join("");
}
function stockList(){
 const q=$("#search").value.toLowerCase(),cat=$("#industry").value,alerts=$("#onlyAlerts").checked;
 const rows=state.stocks.filter(s=>(!q||(s.ticker+" "+s.name+" "+s.sector).toLowerCase().includes(q))&&(!cat||s.sector===cat)&&(!alerts||s.signals?.length));
 rows.sort((a,b)=>Number(b.signals?.some(x=>x.priority==="high"))-Number(a.signals?.some(x=>x.priority==="high"))||Number(b.signals?.length>0)-Number(a.signals?.length>0)||a.ticker.localeCompare(b.ticker));
 $("#stockCount").textContent=rows.length+" listed";
 $("#stockList").innerHTML=rows.map(s=>'<button type="button" class="pv-stock '+(state.selected===s.ticker?"active":"")+'" data-stock="'+esc(s.ticker)+'"><span><b>'+esc(s.ticker)+'</b><small>'+esc(s.name)+'</small><small>'+esc(s.sector)+'</small></span><span class="pv-stock-values"><strong>₹'+fmt(s.lastClose)+'</strong><small>Volume '+fmt(s.indicators?.volumeRatio20)+'×</small><i>'+esc(s.dataStatus||"unavailable")+'</i></span></button>').join("")||'<div class="pv-empty">No symbols match. Try another industry or disable the alert filter.</div>';
}
function chart(s){
 const rows=(s.recentBars||[]).slice(-state.days);
 if(rows.length<12)return'<div class="pv-empty">Not enough comparable daily price and volume bars for a chart.</div>';
 const W=890,x0=47,x1=872,lo=Math.min(...rows.map(x=>x.low))*.988,hi=Math.max(...rows.map(x=>x.high))*1.015,maxV=Math.max(...rows.map(x=>x.volume),1),n=rows.length;
 const x=i=>x0+(x1-x0)*i/(n-1),y=p=>235-(p-lo)/Math.max(1,hi-lo)*200;
 const path=rows.map((a,i)=>(i?"L":"M")+x(i).toFixed(1)+","+y(a.close).toFixed(1)).join(" ");
 const grid=[0,.25,.5,.75,1].map(t=>'<line x1="'+x0+'" x2="'+x1+'" y1="'+(235-t*200)+'" y2="'+(235-t*200)+'" stroke="#355568" stroke-dasharray="3,5"/><text x="40" y="'+(239-t*200)+'" text-anchor="end" fill="#9ebdca" font-size="10">'+fmt(lo+t*(hi-lo))+'</text>').join("");
 const vol=rows.map((r,i)=>{const height=r.volume/maxV*76,w=Math.max(2,(x1-x0)/n*.65);return'<rect x="'+(x(i)-w/2).toFixed(1)+'" y="'+(339-height).toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+height.toFixed(1)+'" fill="'+(i&&r.close<rows[i-1].close?"#d99691":"#67d9ba")+'" opacity=".7"><title>'+esc(r.date)+': ₹'+fmt(r.close)+' / '+fmt(r.volume)+' shares</title></rect>'}).join("");
 const levels=[["SMA20",s.indicators?.sma20,"#f3c782"],["SMA50",s.indicators?.sma50,"#9fbcec"],["SMA200",s.indicators?.sma200,"#e6b4dd"]].filter(v=>v[1]!=null&&v[1]>=lo&&v[1]<=hi).map(v=>'<line x1="'+x0+'" x2="'+x1+'" y1="'+y(v[1]).toFixed(1)+'" y2="'+y(v[1]).toFixed(1)+'" stroke="'+v[2]+'" stroke-dasharray="5,7"/><text x="'+x1+'" y="'+(y(v[1])-5).toFixed(1)+'" font-size="10" fill="'+v[2]+'" text-anchor="end">'+v[0]+' ₹'+fmt(v[1])+'</text>').join("");
 return'<div class="pv-legend"><span>● Price (₹)</span><span>▮ Volume (shares)</span><span>— Moving-average reference levels</span></div><svg viewBox="0 0 900 366" role="img" aria-label="Daily close and daily share volume from '+esc(rows[0].date)+' to '+esc(rows.at(-1).date)+'">'+grid+'<path d="'+path+'" stroke="#66dfba" stroke-width="2.6" fill="none"/>'+levels+'<line x1="'+x0+'" x2="'+x1+'" y1="258" y2="258" stroke="#48687a"/>'+vol+'<text x="'+x0+'" y="359" fill="#9fbac8" font-size="11">'+esc(rows[0].date)+'</text><text x="'+x1+'" y="359" text-anchor="end" fill="#9fbac8" font-size="11">'+esc(rows.at(-1).date)+'</text></svg>';
}
function detail(){
 const s=state.stocks.find(x=>x.ticker===state.selected);
 if(!s){$("#stockDetail").innerHTML='<div class="pv-empty">No stock data published yet.</div>';return;}
 const i=s.indicators||{},warn=!good(s)||s.dataQuality?.signalsWithheld;
 const header='<div class="pv-section-head"><div><small>'+esc(s.sector||"")+" · "+esc(s.asOf||"date unavailable")+'</small><h2>'+esc(s.name||s.ticker)+' <span class="pv-symbol">'+esc(s.ticker)+'</span></h2><p>'+esc(s.trend||"No trend inference")+' · '+esc(s.observations||0)+' daily bars</p></div><span class="pv-tag">'+esc(s.dataStatus||"unavailable")+'</span></div>';
 const metrics=[["Close","₹"+fmt(s.lastClose)],["Rel volume",fmt(i.volumeRatio20)+"×"],["20D return",sign(i.return20dPct)],["60D return",sign(i.return60dPct)],["CMF 20",fmt(i.cmf20)],["OBV volume proxy",fmt(i.obv20Scaled)],["50D SMA","₹"+fmt(i.sma50)],["200D SMA","₹"+fmt(i.sma200)]].map(a=>'<div class="pv-metric"><small>'+esc(a[0])+'</small><b>'+esc(a[1])+'</b></div>').join("");
 const signals=warn?'<div class="pv-caution">Active alerts withheld: data are partial, stale, unavailable or affected by recent split/large price gap. '+esc(s.sourceFetchError||"")+'</div>':
 (s.signals||[]).length?(s.signals||[]).map(x=>'<article class="pv-alert"><div class="pv-tag '+(x.priority==="high"?"pv-important":"")+'">'+esc(x.priority)+'</div><h3>'+esc(x.headline)+'</h3><p><b>Observed:</b> '+esc(x.evidence)+'</p><p><b>Confirmation:</b> '+esc(x.confirmation)+'</p><p><b>Invalidation:</b> '+esc(x.invalidation)+'</p></article>').join(""):'<div class="pv-empty">No configured price–volume pattern triggered. Absence of an alert is not an investment conclusion.</div>';
 const source=/^https:\/\//.test(s.sourceUrl||"")?'<a target="_blank" rel="noopener" href="'+esc(s.sourceUrl)+'">View chart source ↗</a>':'No validated source link';
 $("#stockDetail").innerHTML='<div class="pv-panel">'+header+'<div class="pv-metrics">'+metrics+'</div><small>Source: '+esc(s.source||"unavailable")+' · '+source+'</small></div><div class="pv-panel"><div class="pv-section-head"><h2>Price and volume history</h2><div class="pv-periods"><button data-period="20" '+(state.days===20?'class="active"':"")+'>1M</button><button data-period="60" '+(state.days===60?'class="active"':"")+'>3M</button><button data-period="120" '+(state.days===120?'class="active"':"")+'>6M</button></div></div>'+chart(s)+'</div><div class="pv-panel"><h2>Why this stock might need attention</h2>'+signals+'</div><div class="pv-panel"><h2>Short / long-run context</h2><div class="pv-comparison"><p><b>Short run:</b> 20-session return '+sign(i.return20dPct)+', relative volume '+fmt(i.volumeRatio20)+'×, RSI '+fmt(i.rsi14)+'.</p><p><b>Long run:</b> 60-session return '+sign(i.return60dPct)+', 200-DMA ₹'+fmt(i.sma200)+', distance to 52-week high '+sign(i.distance52wHighPct)+'.</p></div><p class="pv-note">A short-term breakout below a declining long-term trend merits closer investigation, not a buy decision. Corroborate with fundamentals, sector leadership, corporate actions and valuation.</p></div>';
 $$("#stockDetail [data-period]").forEach(b=>b.onclick=()=>{state.days=Number(b.dataset.period);detail()});
}
async function load(){
 $("#timestamp").textContent="Fetching published market-signal snapshot…";
 try{
  const r=await fetch("./data/market-signals/stock-price-volume.json?t="+Date.now(),{cache:"no-store"});
  if(!r.ok)throw Error("source not published (HTTP "+r.status+")");
  const d=await r.json();state.stocks=d.stocks||[];
  $("#timestamp").textContent=(d.generatedAt||"").slice(0,16).replace("T"," ")+" UTC · "+esc(d.status)+" · Unofficial daily OHLCV mirror";
  universe();stockList();detail();
 }catch(err){
  $("#timestamp").textContent="Data unavailable: "+String(err);
  $("#stockDetail").innerHTML='<div class="pv-caution">No valid price-volume feed published yet. Check GitHub Actions; no signals will be invented.</div>';
 }
}
$("#search").addEventListener("input",stockList);
$("#industry").addEventListener("change",stockList);
$("#onlyAlerts").addEventListener("change",stockList);
$("#stockList").addEventListener("click",ev=>{
 const b=ev.target.closest("[data-stock]");if(!b)return;
 state.selected=b.dataset.stock;history.replaceState(null,"","#"+encodeURIComponent(state.selected));stockList();detail();
});
$("#refresh").addEventListener("click",load);
const hash=decodeURIComponent(location.hash.slice(1)).toUpperCase();
if(hash)state.selected=hash;
load();
})();