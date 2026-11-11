/* Equity Atlas global site navigation. No dependencies, no external UI network calls, no tracking. */
(function(){
"use strict";
const PAGES=[
 {name:"Company Research",url:"./index.html",group:"RESEARCH",file:"index.html"},
 {name:"Sector Intelligence",url:"./sector-intelligence.html",group:"RESEARCH",file:"sector-intelligence.html"},
 {name:"Price × Volume",url:"./company-signals.html",group:"RESEARCH",file:"company-signals.html"},
 {name:"Morning Intelligence",url:"./market-desk.html",group:"MARKETS",file:"market-desk.html"},
 {name:"Rotation × Odds",url:"./signals.html",group:"MARKETS",file:"signals.html"},
 {name:"News Archive",url:"./news-radar.html",group:"MARKETS",file:"news-radar.html"}
];
function init(){
 const main=document.querySelector("main.main")||document.querySelector("main");
 if(!main||document.querySelector(".ea-universal"))return;
 const pathname=window.location.pathname.split("/").pop()||"index.html";
 const skip=document.createElement("a");skip.href="#ea-primary";skip.className="ea-skip";skip.textContent="Skip navigation to page content";
 document.body.insertBefore(skip,document.body.firstChild);
 main.id=main.id||"ea-primary";main.setAttribute("tabindex","-1");
 const bar=document.createElement("nav");
 bar.className="ea-universal";bar.setAttribute("aria-label","Equity Atlas main sections");
 const group=(name)=>{
  const div=document.createElement("div");div.className="ea-group";
  const tag=document.createElement("span");tag.className="ea-group-label";tag.textContent=name;
  div.appendChild(tag);
  PAGES.filter(p=>p.group===name).forEach(p=>{
   const anchor=document.createElement("a");anchor.href=p.url;anchor.textContent=p.name;anchor.className="ea-nav-link";
   if(p.file===pathname)anchor.setAttribute("aria-current","page");
   div.appendChild(anchor);
  });
  return div;
 };
 const left=document.createElement("div");left.className="ea-group";
 left.appendChild(group("RESEARCH"));left.appendChild(group("MARKETS"));bar.appendChild(left);
 const right=document.createElement("div");right.className="ea-nav-right";
 const cycle=document.createElement("span");cycle.className="ea-cycle";
 cycle.textContent="Refresh targets · 07:00 / 19:00 IST";cycle.title="Collection jobs are scheduled; data availability may lag if the source or runner is delayed";
 right.appendChild(cycle);
 const btn=document.createElement("button");btn.type="button";btn.className="ea-theme";btn.setAttribute("aria-label","Toggle display between dark and paper modes");
 function themeLabel(){btn.textContent=document.documentElement.dataset.atlasTheme==="paper"?"☾ Dark":"☀ Paper"}
 btn.addEventListener("click",()=>{
  const mode=document.documentElement.dataset.atlasTheme==="paper"?"dark":"paper";
  document.documentElement.dataset.atlasTheme=mode;
  try{localStorage.setItem("equity-atlas-theme",mode)}catch(_){}
  themeLabel();
 });
 try{const saved=localStorage.getItem("equity-atlas-theme");if(saved==="paper")document.documentElement.dataset.atlasTheme="paper"}catch(_){}
 themeLabel();right.appendChild(btn);bar.appendChild(right);
 main.insertBefore(bar,main.firstChild);
 // Home research queue: company technical signals, with source dates shown.
 if(pathname==="index.html"){
  const overview=document.querySelector("#overview");
  if(overview){
   const panel=document.createElement("section");panel.className="ea-home-hub";
   panel.innerHTML='<div><div class="ea-group-label">RESEARCH DESK / PRICE × VOLUME</div><strong>Company signal surveillance</strong><p>Technical patterns are research leads, not buy calls. Daily bar freshness is shown per symbol.</p><div class="ea-home-alerts" id="ea-home-alerts">Loading published stock observations…</div></div><a class="ea-home-cta" href="./company-signals.html">Open technical research ↗</a>';
   overview.insertBefore(panel,overview.firstChild);
   fetch("./data/market-signals/stock-price-volume.json?t="+Date.now(),{cache:"no-store"}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(data=>{
    const target=document.getElementById("ea-home-alerts");if(!target)return;
    const valid=(data.stocks||[]).filter(s=>s.dataStatus==="ready"&&s.signals?.length);
    target.textContent="";
    if(!valid.length){target.textContent="No currently verified high-priority signals; check latest source dates.";return}
    valid.slice(0,4).forEach(s=>{
     const a=document.createElement("a");
     a.href="./company-signals.html#"+encodeURIComponent(s.ticker);
     a.className="ea-signal-link";
     a.textContent=s.ticker+" · "+s.signals[0].priority.toUpperCase()+" · bars "+s.asOf;
     target.appendChild(a);
    });
   }).catch(()=>{const t=document.getElementById("ea-home-alerts");if(t)t.textContent="Price-volume dataset not yet available";});
  }
 }
 const foot=document.createElement("div");foot.className="ea-page-footer";
 foot.textContent="Equity Atlas · Evidence-first research; figures are as of their displayed source date. ";
 const a=document.createElement("a");a.href="./market-desk.html#sources";a.textContent="Source coverage & limitations";foot.appendChild(a);
 main.appendChild(foot);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
else init();
})();