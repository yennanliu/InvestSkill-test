"""Page shell + shared CSS for the showcase (matches docs/index.html tokens)."""

CSS = r"""
:root{
  --green:#00b14f; --green-press:#009644; --green-wash:#e6f7ee; --green-band:#00692e;
  --amber:#ff8c00; --amber-ink:#b35c00; --red:#e02020; --red-ink:#c0161c;
  --white:#fff; --ink:#16181a; --ink-2:#4a4f55; --ink-3:#767c85;
  --line:#e6e8eb; --surface:#f7f8f9;
  --s-4:4px; --s-8:8px; --s-12:12px; --s-16:16px; --s-24:24px; --s-32:32px;
  --s-48:48px; --s-64:64px; --s-80:80px;
  --r-btn:8px; --r-card:16px; --r-pill:999px;
  --shadow:0 2px 8px rgba(22,24,26,.08); --shadow-lift:0 8px 24px rgba(22,24,26,.12);
  --shadow-hi:0 16px 40px rgba(0,86,40,.16);
  --ease:cubic-bezier(.22,1,.36,1); --dur:.6s;
  --sans:"Inter","Poppins",-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",
         "PingFang TC","Microsoft JhengHei",Roboto,Helvetica,Arial,sans-serif;
  --display:"Poppins","Inter",-apple-system,BlinkMacSystemFont,"Noto Sans TC",
         "PingFang TC","Microsoft JhengHei",Segoe UI,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,"Cascadia Mono","Liberation Mono",monospace;
  --wrap:1220px;
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:84px}
body{margin:0;background:var(--white);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.75;-webkit-font-smoothing:antialiased}
img,svg{max-width:100%;display:block}
a{color:var(--green-band);text-decoration:none}
a:hover{text-decoration:underline}
h1,h2,h3,h4{font-family:var(--display);line-height:1.25;letter-spacing:-.01em;margin:0}
h1{font-size:clamp(1.9rem,4.4vw,2.9rem);font-weight:800;letter-spacing:-.02em}
h2{font-size:clamp(1.45rem,2.7vw,2rem);font-weight:800;letter-spacing:-.02em}
h3{font-size:1.16rem;font-weight:700}
h4{font-size:1rem;font-weight:700}
p{margin:0}
.wrap{max-width:var(--wrap);margin-inline:auto;padding-inline:var(--s-24)}

/* ---------- nav ---------- */
.nav{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.94);
  backdrop-filter:saturate(180%) blur(12px);border-bottom:1px solid var(--line);
  transition:box-shadow .24s ease,background .24s ease}
.nav.stuck{box-shadow:0 6px 22px rgba(22,24,26,.08);background:rgba(255,255,255,.97)}
.nav__in{display:flex;align-items:center;gap:var(--s-16);height:68px;min-width:0}
/* reading-progress rail, welded to the nav's bottom edge (sticky nav is the
   containing block, so this spans the viewport rather than the wrap) */
.prog{position:absolute;left:0;right:0;bottom:-1px;height:2px;overflow:hidden;pointer-events:none}
.prog i{display:block;height:100%;width:0;border-radius:0 2px 2px 0;
  background:linear-gradient(90deg,var(--green-band),var(--green) 60%,#7ee2a8)}
.brand{display:flex;align-items:center;gap:var(--s-12);min-width:0;text-decoration:none;
  font-family:var(--display);font-weight:800;letter-spacing:-.02em;white-space:nowrap;color:var(--ink)}
.brand:hover{text-decoration:none}
.brand__text{overflow:hidden;text-overflow:ellipsis}
.brand__mark{width:32px;height:32px;border-radius:var(--r-btn);background:var(--green);
  display:grid;place-items:center;flex:0 0 auto}
.nav__links{display:none;gap:var(--s-24);margin-left:auto;font-size:.875rem;font-weight:600}
.nav__links a{position:relative;text-decoration:none;color:var(--ink-2);padding-block:var(--s-8);
  transition:color .18s ease}
.nav__links a:hover,.nav__links a[aria-current="page"]{color:var(--green)}
.nav__links a::after{content:"";position:absolute;left:0;right:0;bottom:2px;height:2px;border-radius:2px;
  background:var(--green);transform:scaleX(0);transform-origin:left;transition:transform .24s var(--ease)}
.nav__links a:hover::after,.nav__links a[aria-current="page"]::after{transform:scaleX(1)}
.nav__cta{margin-left:auto;flex:0 0 auto}
@media(min-width:1000px){.nav__links{display:flex}.nav__cta{margin-left:0}}
@media(max-width:559px){.nav__cta-label{display:none}.brand{font-size:.875rem}}
.btn{display:inline-flex;align-items:center;gap:var(--s-8);padding:14px 24px;border:0;
  border-radius:var(--r-btn);background:var(--green);color:#fff;font-family:var(--display);
  font-size:1rem;font-weight:700;text-decoration:none;cursor:pointer;
  transition:background .16s ease,transform .1s ease}
.btn:hover{background:var(--green-press);text-decoration:none}
.btn:active{transform:scale(.98)}
.btn:focus-visible{outline:3px solid var(--green-band);outline-offset:2px}
.btn--sm{padding:10px 18px;font-size:.875rem}
.btn--soft{background:var(--green-wash);color:var(--green-band)}
.btn--soft:hover{background:#d3f0e0}
.btn--onband{background:#fff;color:var(--green-band)}
.btn--onband:hover{background:#eef8f2}
.btn--ghost{background:transparent;color:#fff;box-shadow:inset 0 0 0 2px rgba(255,255,255,.55)}
.btn--ghost:hover{background:rgba(255,255,255,.12)}

/* ---------- hero ---------- */
.rhero{position:relative;overflow:hidden;color:#fff;
  background:radial-gradient(120% 140% at 88% 8%,rgba(0,177,79,.95) 0%,rgba(0,177,79,0) 58%),
  linear-gradient(104deg,var(--green-band) 0%,#007d38 52%,#009243 100%)}
/* ::before = slow-drifting aurora; ::after = scrim (contrast guarantee) plus a
   barely-there moving hatch. Both are decoration only, so no markup carries them. */
.rhero::before{content:"";position:absolute;top:-45%;right:-12%;width:74%;height:190%;
  pointer-events:none;border-radius:50%;
  background:radial-gradient(closest-side,rgba(126,226,168,.40),rgba(126,226,168,0) 72%);
  animation:drift 24s ease-in-out infinite alternate}
.rhero::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(90deg,rgba(0,58,26,.55) 0%,rgba(0,58,26,.18) 42%,rgba(0,58,26,0) 72%),
    repeating-linear-gradient(115deg,rgba(255,255,255,.055) 0 1px,rgba(255,255,255,0) 1px 26px);
  background-position:0 0,0 0;animation:hatch 40s linear infinite}
.rhero__in{position:relative;z-index:1;padding-block:var(--s-48) var(--s-64)}
.rhero .eyebrow{color:#9ce8bd}
.rhero__sub{margin-top:var(--s-16);font-size:1.06rem;max-width:62ch;color:rgba(255,255,255,.93)}
.eyebrow{font-family:var(--display);font-size:.8125rem;font-weight:700;letter-spacing:.08em;
  text-transform:uppercase;color:var(--green);margin-bottom:var(--s-8)}
.eyebrow::before{content:"";display:inline-block;width:20px;height:2px;border-radius:2px;
  background:currentColor;vertical-align:.22em;margin-right:9px;opacity:.85}
.chips{display:flex;flex-wrap:wrap;gap:var(--s-8);margin-top:var(--s-24)}
.chip{display:inline-flex;align-items:center;gap:6px;padding:6px 13px;border-radius:var(--r-pill);
  background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.30);
  font-size:.8125rem;font-weight:600;color:#fff;white-space:nowrap}
.chip--ink{background:var(--green-wash);border-color:#b9e7cf;color:var(--green-band)}

/* ---------- layout ---------- */
.shell{display:block;padding-block:var(--s-48) var(--s-80)}
@media(min-width:1060px){
  .shell{display:grid;grid-template-columns:246px minmax(0,1fr);gap:var(--s-48);align-items:start}
}
.toc{display:none}
@media(min-width:1060px){
  .toc{display:block;position:sticky;top:92px;max-height:calc(100vh - 116px);overflow-y:auto;
    font-size:.8125rem;border-left:2px solid var(--line);padding-left:var(--s-16)}
}
.toc__h{font-family:var(--display);font-weight:800;font-size:.75rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:var(--s-12)}
.toc a{display:block;padding:5px 0;color:var(--ink-2);text-decoration:none;line-height:1.4}
.toc a:hover{color:var(--green);text-decoration:none}
.toc a.on{color:var(--green-band);font-weight:700}
.toc__grp{margin-top:var(--s-16);font-size:.6875rem;font-weight:700;letter-spacing:.06em;
  text-transform:uppercase;color:var(--ink-3)}
.doc>section{padding-block:var(--s-32);border-top:1px solid var(--line)}
.doc>section:first-child{border-top:0;padding-top:0}
.doc h2{margin-bottom:var(--s-8)}
.doc h3{margin:var(--s-32) 0 var(--s-12)}
.doc h4{margin:var(--s-24) 0 var(--s-8)}
.doc p{margin-block:var(--s-12)}
.doc ul,.doc ol{margin:var(--s-12) 0;padding-left:1.35em}
.doc li{margin-block:6px}
.modnum{display:inline-grid;place-items:center;width:29px;height:29px;border-radius:8px;
  background:var(--green-wash);color:var(--green-band);font-family:var(--display);
  font-weight:800;font-size:.8125rem;margin-right:10px;vertical-align:3px}
.skilltag{display:inline-block;font-family:var(--mono);font-size:.75rem;font-weight:600;
  background:var(--surface);border:1px solid var(--line);border-radius:var(--r-pill);
  padding:3px 11px;color:var(--ink-2);margin-left:6px;vertical-align:2px;white-space:nowrap}
.lede{font-size:1.06rem;color:var(--ink-2)}

/* ---------- cards / tiles ---------- */
.grid{display:grid;gap:var(--s-16)}
.g2{grid-template-columns:repeat(auto-fit,minmax(272px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(216px,1fr))}
.g4{grid-template-columns:repeat(auto-fit,minmax(174px,1fr))}
.card{background:var(--white);border:1px solid var(--line);border-radius:var(--r-card);
  padding:var(--s-24);box-shadow:var(--shadow);
  transition:transform .24s var(--ease),box-shadow .24s var(--ease),border-color .24s ease}
.card--wash{background:var(--green-wash);border-color:#b9e7cf}
.card--surface{background:var(--surface)}
.card__h{font-family:var(--display);font-weight:800;font-size:1rem;margin-bottom:var(--s-8)}
/* only cards that are links lift — a static card that moves under the cursor lies */
a.card{position:relative;overflow:hidden}
a.card::before{content:"";position:absolute;left:0;top:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--green-band),var(--green) 55%,#7ee2a8);
  transform:scaleX(0);transform-origin:left;transition:transform .34s var(--ease)}
a.card:hover,a.card:focus-visible{transform:translateY(-4px);box-shadow:var(--shadow-hi);
  border-color:#b9e7cf;text-decoration:none}
a.card:hover::before,a.card:focus-visible::before{transform:scaleX(1)}
.tile{background:var(--white);border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s-16) var(--s-16);
  transition:transform .24s var(--ease),box-shadow .24s var(--ease)}
.tile:hover{transform:translateY(-3px);box-shadow:var(--shadow-lift)}
.tile__k{font-size:.75rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--ink-3)}
.tile__v{font-family:var(--display);font-size:1.6rem;font-weight:800;line-height:1.2;margin-top:4px;
  letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.tile__n{font-size:.75rem;color:var(--ink-3);margin-top:3px;line-height:1.45}
.up{color:var(--green-band)} .dn{color:var(--red-ink)} .fl{color:var(--amber-ink)}

/* status pills — always icon + text, never colour alone */
.st{display:inline-flex;align-items:center;gap:5px;padding:3px 11px;border-radius:var(--r-pill);
  font-size:.75rem;font-weight:700;white-space:nowrap;border:1px solid}
.st--good{background:var(--green-wash);color:var(--green-band);border-color:#b9e7cf}
.st--warn{background:#fff4e5;color:var(--amber-ink);border-color:#ffd9a8}
.st--bad{background:#fdeaea;color:var(--red-ink);border-color:#f7c4c4}
.st--neut{background:var(--surface);color:var(--ink-2);border-color:var(--line)}

/* ---------- tables ---------- */
.tblwrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-block:var(--s-16)}
table{border-collapse:collapse;width:100%;font-size:.875rem;font-variant-numeric:tabular-nums}
.dt th,.dt td,.heat th,.heat td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
.dt thead th,.heat thead th{background:var(--surface);font-family:var(--display);font-weight:700;
  font-size:.8125rem;color:var(--ink-2);border-bottom:2px solid var(--line);white-space:nowrap;
  position:sticky;top:0}
.dt tbody th,.heat tbody th{font-weight:600;text-align:left}
.dt tbody tr:hover{background:#fafbfb}
.heat td{text-align:center;font-weight:700;font-size:.8125rem;border:2px solid #fff}
.heat tbody th{background:var(--surface);white-space:nowrap;font-size:.8125rem}
.dt--sm{font-size:.8125rem}
.dt--sm th,.dt--sm td{padding:7px 10px}
caption{caption-side:top;text-align:left;font-size:.8125rem;color:var(--ink-3);padding-bottom:var(--s-8)}

/* ---------- figures ---------- */
.fig{margin:var(--s-24) 0}
.figbox{background:var(--white);border:1px solid var(--line);border-radius:var(--r-card);
  padding:var(--s-16);overflow-x:auto;position:relative}
.chart{width:100%;height:auto;min-width:min(100%,560px)}
figcaption{font-size:.8125rem;color:var(--ink-2);margin-top:var(--s-8);font-weight:600}
.fignote{font-size:.75rem;color:var(--ink-3);margin-top:4px;line-height:1.6}
.lgd{display:flex;flex-wrap:wrap;gap:var(--s-16);margin-bottom:var(--s-12);font-size:.8125rem;font-weight:600;color:var(--ink-2)}
.lgd__i{display:inline-flex;align-items:center;gap:6px}
.lgd__sw{width:12px;height:12px;border-radius:3px;flex:0 0 auto}
.tblview{margin-top:var(--s-8)}
.tblview summary{cursor:pointer;font-size:.8125rem;font-weight:700;color:var(--green-band);
  padding:5px 0;list-style:none;display:inline-flex;align-items:center;gap:5px}
.tblview summary::before{content:"▸";transition:transform .15s}
.tblview[open] summary::before{transform:rotate(90deg)}
.tblview summary::-webkit-details-marker{display:none}
.ch-tip{position:absolute;pointer-events:none;background:var(--ink);color:#fff;font-size:12px;
  line-height:1.55;padding:8px 11px;border-radius:8px;box-shadow:var(--shadow-lift);
  white-space:nowrap;opacity:0;transition:opacity .1s;z-index:5;font-variant-numeric:tabular-nums}
.ch-tip b{font-weight:700}
.ch-tip .r{display:flex;align-items:center;gap:6px;margin-top:3px}
.ch-tip .sw{width:9px;height:9px;border-radius:2px;flex:0 0 auto}

/* ---------- callouts ---------- */
.call{border-left:4px solid var(--green);background:var(--green-wash);padding:var(--s-16) var(--s-24);
  border-radius:0 var(--r-card) var(--r-card) 0;margin-block:var(--s-24)}
.call--warn{border-color:var(--amber);background:#fff8ef}
.call--bad{border-color:var(--red);background:#fdf0f0}
.call--ink{border-color:var(--ink-3);background:var(--surface)}
.call__h{font-family:var(--display);font-weight:800;font-size:.9375rem;margin-bottom:6px;
  display:flex;align-items:center;gap:7px}
.call p{margin-block:6px;font-size:.9375rem}
.call ul{margin:6px 0;font-size:.9375rem}

/* signal block — the InvestSkill house style, kept monospace */
.sig{position:relative;background:linear-gradient(158deg,#0f1113 0%,#151b1e 100%);color:#e8edf1;
  border-radius:var(--r-card);padding:var(--s-24);box-shadow:inset 0 0 0 1px rgba(126,226,168,.16);
  font-family:var(--mono);font-size:.8125rem;line-height:1.85;overflow-x:auto;margin-block:var(--s-24)}
.sig::before{content:"";position:absolute;left:0;top:0;right:0;height:2px;pointer-events:none;
  border-radius:var(--r-card) var(--r-card) 0 0;background-repeat:no-repeat;background-size:38% 100%;
  background-image:linear-gradient(90deg,rgba(126,226,168,0),#7ee2a8,rgba(126,226,168,0));
  animation:sheen 5.5s linear infinite}
.sig b{color:#7ee2a8;font-weight:700}
.sig .k{color:#8b98a5}
.sig pre{margin:0;font:inherit}
.mm{font-family:var(--mono);font-size:.8125rem;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--r-btn);padding:var(--s-16);overflow-x:auto;line-height:1.7}
.mm pre{margin:0;font:inherit}
code{font-family:var(--mono);font-size:.9em;background:var(--surface);border:1px solid var(--line);
  border-radius:5px;padding:1px 5px}
.doc pre code{border:0;background:none;padding:0}

/* ---------- flow / chain diagram ---------- */
.flow{display:grid;gap:var(--s-12);margin-block:var(--s-24)}
.flow__row{display:grid;gap:var(--s-12);grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}
.node{border:1px solid var(--line);border-radius:12px;padding:var(--s-12) var(--s-16);background:#fff;
  box-shadow:var(--shadow);position:relative;
  transition:transform .22s var(--ease),box-shadow .22s var(--ease)}
.node:hover{transform:translateY(-3px);box-shadow:var(--shadow-lift);z-index:2}
.node--choke{border-color:var(--red);border-width:2px;background:#fdf0f0}
.node--target{border-color:var(--green);border-width:2px;background:var(--green-wash)}
.node__pos{font-size:.6875rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3)}
.node__n{font-family:var(--display);font-weight:800;font-size:.9375rem;margin-top:2px}
.node__t{font-family:var(--mono);font-size:.75rem;color:var(--ink-2);margin-top:5px;line-height:1.6}
.node__m{font-size:.6875rem;color:var(--ink-3);margin-top:5px}
.arrowrow{text-align:center;color:var(--ink-3);font-size:1.1rem;line-height:1}

/* ---------- stepper: a workflow chain as a rail of numbered steps ---------- */
.stp{position:relative;display:grid;gap:var(--s-8);margin-block:var(--s-16);padding-left:38px}
.stp::before{content:"";position:absolute;left:15px;top:14px;bottom:16px;width:2px;border-radius:2px;
  background:linear-gradient(180deg,var(--stp-c,var(--green)),rgba(118,124,133,.28));
  transform-origin:top;transform:scaleY(1)}
.js .stp::before{transform:scaleY(0);transition:transform .8s var(--ease) .1s}
.js .stp.in::before{transform:scaleY(1)}
.stp__i{position:relative;background:#fff;border:1px solid var(--line);border-radius:12px;
  padding:9px 14px;box-shadow:var(--shadow);
  transition:transform .2s var(--ease),box-shadow .2s var(--ease),border-color .2s ease}
.stp__i:hover{transform:translateX(3px);box-shadow:var(--shadow-lift);border-color:#b9e7cf}
.stp__i::before{content:attr(data-n);position:absolute;left:-38px;top:8px;width:26px;height:26px;
  border-radius:50%;display:grid;place-items:center;background:var(--stp-c,var(--green));color:#fff;
  font-family:var(--display);font-size:.75rem;font-weight:800;
  box-shadow:0 0 0 3px #fff,0 0 0 4px rgba(0,177,79,.16)}
.stp__i--gate::before{background:var(--red)}
.stp__i--gate{border-color:#f7c4c4;background:#fdf0f0}
.stp__s{font-family:var(--mono);font-size:.8125rem;font-weight:700;color:var(--ink)}
.stp__w{font-size:.75rem;color:var(--ink-2);margin-top:2px;line-height:1.55}

/* ---------- flow diagrams (SVG) ---------- */
.dagfig .figbox{background:linear-gradient(180deg,#fcfdfd,#f7f8f9)}
/* flow diagrams are wider than the data charts; keep their labels legible and let
   the figbox scroll rather than shrinking 10px type into nothing */
.dagfig .chart{min-width:min(100%,820px)}
.fl-dash{stroke-dasharray:5 7;animation:dashflow 1.1s linear infinite}
.fl-pulse{animation:pulse 2.6s ease-in-out infinite}
.fl-node{transition:transform .2s var(--ease)}
.fl-cell{transition:opacity .2s ease,transform .2s ease;transform-origin:center;transform-box:fill-box}
.fl-cell:hover{transform:scale(1.35)}
.js .dagfig .fl-node,.js .dagfig .fl-cell{opacity:0}
.js .dagfig.in .fl-node{animation:pop .5s var(--ease) forwards}
/* cells fade only — an animated transform would out-rank the :hover scale above */
.js .dagfig.in .fl-cell{animation:fade .45s ease forwards}
.js .dagfig .fl-dash{opacity:0}
.js .dagfig.in .fl-dash{animation:dashflow 1.1s linear infinite,fade .5s ease .35s forwards}

/* ---------- motion system ---------- */
@keyframes drift{
  0%{transform:translate3d(0,0,0) scale(1)}
  50%{transform:translate3d(-5%,4%,0) scale(1.1)}
  100%{transform:translate3d(4%,-3%,0) scale(1.04)}}
@keyframes hatch{to{background-position:0 0,-520px 0}}
@keyframes dashflow{to{stroke-dashoffset:-24}}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes pulse{0%,100%{opacity:.30}50%{opacity:.85}}
@keyframes pop{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes sheen{from{background-position:-45% 0}to{background-position:145% 0}}

/* scroll reveal — the .js gate means no-JS readers get everything, unanimated */
.js .rv{opacity:0;transform:translateY(18px);
  transition:opacity var(--dur) var(--ease),transform var(--dur) var(--ease)}
.js .rv.in{opacity:1;transform:none}

/* charts draw themselves once their figure scrolls in (pathLength=1 → dash maths
   is exact regardless of the path's real length) */
.js .fig .ch-draw,.js .fig .g-arc{stroke-dasharray:1 1;stroke-dashoffset:1}
.js .fig.in .ch-draw{animation:draw 1.5s var(--ease) .08s forwards}
.js .fig.in .g-arc{animation:draw 1.1s var(--ease) .12s forwards}

/* back-to-top */
.totop{position:fixed;right:16px;bottom:16px;z-index:40;width:44px;height:44px;border-radius:50%;
  display:grid;place-items:center;background:var(--green);color:#fff;box-shadow:var(--shadow-lift);
  opacity:0;visibility:hidden;transform:translateY(12px) scale(.9);
  transition:opacity .26s var(--ease),transform .26s var(--ease),visibility .26s,background .16s}
.totop.on{opacity:1;visibility:visible;transform:none}
.totop:hover{background:var(--green-press);text-decoration:none}
.totop:focus-visible{outline:3px solid var(--green-band);outline-offset:3px}

/* ---------- misc ---------- */
.band{background:var(--green-band);color:#fff;padding-block:var(--s-48)}
.band a{color:#fff}
.section--wash{background:var(--green-wash)}
.section--surface{background:var(--surface)}
.section{padding-block:var(--s-64)}
.foot{border-top:1px solid var(--line);padding-block:var(--s-32);font-size:.8125rem;color:var(--ink-3)}
.foot a{color:var(--ink-2)}
.disc{font-size:.75rem;color:var(--ink-3);line-height:1.7;background:var(--surface);
  border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s-16);margin-top:var(--s-24)}
.crumb{font-size:.8125rem;color:rgba(255,255,255,.8);margin-bottom:var(--s-12)}
.crumb a{color:rgba(255,255,255,.92)}
.skip{position:absolute;left:-9999px}
.skip:focus{left:var(--s-16);top:var(--s-8);z-index:60;background:#fff;color:var(--ink);
  padding:10px 16px;border-radius:var(--r-btn);box-shadow:var(--shadow-lift)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
/* Motion is decoration: every animated element must also be legible with the
   animation removed. Both guards below assert that, and the dash-array resets
   matter most — a mid-draw chart line with animations off is an invisible line. */
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{animation:none!important;transition:none!important}
  html{scroll-behavior:auto}
  .js .rv{opacity:1!important;transform:none!important}
  .js .dagfig .fl-node,.js .dagfig .fl-cell,.js .dagfig .fl-dash{opacity:1!important}
  .ch-draw,.g-arc{stroke-dasharray:none!important;stroke-dashoffset:0!important}
  .fl-dash{stroke-dasharray:5 7!important}
  .js .stp::before{transform:scaleY(1)!important}
}
@media print{
  .nav,.toc,.tblview,.totop,.prog{display:none}
  .shell{display:block}
  .figbox,.card{break-inside:avoid;box-shadow:none}
  *,*::before,*::after{animation:none!important;transition:none!important}
  .js .rv{opacity:1!important;transform:none!important}
  .js .dagfig .fl-node,.js .dagfig .fl-cell,.js .dagfig .fl-dash{opacity:1!important}
  .ch-draw,.g-arc{stroke-dasharray:none!important;stroke-dashoffset:0!important}
  .js .stp::before{transform:scaleY(1)!important}
  a[href^="http"]::after{content:" (" attr(href) ")";font-size:.7em;color:#666}
}
"""

JS = r"""
// Scroll reveal. Targets are picked here rather than marked up in the HTML so the
// pages stay free of presentational classes; the .js gate in the CSS means a
// reader without JS sees every element in its final state.
(function(){
  var REVEAL='.fig,.dagfig,.card,.tile,.call,.flow,.stp,.sig,.tblwrap,.disc';
  var els=[].slice.call(document.querySelectorAll(REVEAL)).filter(function(el){
    // inside a <details>: display:none never intersects, so it would stay hidden
    return !el.closest('details');
  });
  if(!els.length)return;
  var pid=0,seen={};
  els.forEach(function(el){
    el.classList.add('rv');
    var p=el.parentNode;
    if(!p.__rv)p.__rv=++pid;
    var n=seen[p.__rv]=(seen[p.__rv]||0)+1;
    if(n>1)el.style.transitionDelay=Math.min(n-1,5)*55+'ms';
  });
  if(!('IntersectionObserver' in window)){
    els.forEach(function(el){el.classList.add('in');});
    return;
  }
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(!e.isIntersecting)return;
      e.target.classList.add('in');
      io.unobserve(e.target);
    });
  },{rootMargin:'0px 0px -6% 0px',threshold:.04});
  els.forEach(function(el){io.observe(el);});
})();

// Count-up on headline figures. The element already contains its final text, so
// this only ever replaces a correct value with the same correct value.
(function(){
  var ns=[].slice.call(document.querySelectorAll('[data-count]'));
  if(!ns.length||!('IntersectionObserver' in window))return;
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches)return;
  function run(el){
    var to=parseFloat(el.getAttribute('data-count'));
    if(isNaN(to))return;
    var dp=+(el.getAttribute('data-dp')||0),
        pre=el.getAttribute('data-pre')||'',
        suf=el.getAttribute('data-suf')||'',
        t0=null,D=850;
    function frame(ts){
      if(t0===null)t0=ts;
      var p=Math.min(1,(ts-t0)/D),v=to*(1-Math.pow(1-p,3));
      el.textContent=pre+v.toLocaleString('en-US',
        {minimumFractionDigits:dp,maximumFractionDigits:dp})+suf;
      if(p<1)requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(!e.isIntersecting)return;
      io.unobserve(e.target);
      run(e.target);
    });
  },{threshold:.35});
  ns.forEach(function(n){io.observe(n);});
})();

// Reading progress, nav elevation, back-to-top — one rAF-throttled listener.
(function(){
  var bar=document.querySelector('.prog i'),
      nav=document.querySelector('.nav'),
      top=document.querySelector('.totop'),
      raf=null;
  if(!bar&&!nav&&!top)return;
  function upd(){
    var y=window.scrollY||0,
        h=Math.max(1,document.documentElement.scrollHeight-window.innerHeight);
    if(bar)bar.style.width=Math.min(100,y/h*100).toFixed(2)+'%';
    if(nav)nav.classList.toggle('stuck',y>8);
    if(top)top.classList.toggle('on',y>720);
  }
  addEventListener('scroll',function(){
    if(raf)return;
    raf=requestAnimationFrame(function(){raf=null;upd();});
  },{passive:true});
  addEventListener('resize',upd,{passive:true});
  upd();
})();

// TOC scroll-spy
(function(){
  var links=[].slice.call(document.querySelectorAll('.toc a[href^="#"]'));
  if(!links.length)return;
  var targets=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});
  function upd(){
    var y=window.scrollY+120,cur=-1;
    targets.forEach(function(t,i){if(t&&t.offsetTop<=y)cur=i;});
    links.forEach(function(a,i){a.classList.toggle('on',i===cur);});
  }
  var raf=null;
  addEventListener('scroll',function(){if(raf)return;raf=requestAnimationFrame(function(){raf=null;upd();});},{passive:true});
  upd();
})();

// Line-chart crosshair + tooltip
(function(){
  document.querySelectorAll('svg[data-chart="line"]').forEach(function(svg){
    var holder=svg.parentNode, script=holder.querySelector('.ch-data');
    if(!script)return;
    var cfg=JSON.parse(script.textContent);
    var cross=svg.querySelector('.ch-cross'), cap=svg.querySelector('.ch-cap');
    var tip=document.createElement('div'); tip.className='ch-tip'; holder.appendChild(tip);
    var dots=[];
    var ns='http://www.w3.org/2000/svg';
    cfg.series.forEach(function(s){
      var c=document.createElementNS(ns,'circle');
      c.setAttribute('r','5.5');c.setAttribute('fill',s.colour);
      c.setAttribute('stroke','#fff');c.setAttribute('stroke-width','2');
      c.style.display='none';svg.appendChild(c);dots.push(c);
    });
    function fmt(v){
      var f=cfg.fmt||'{:.0f}';
      var m=f.match(/\{:,?\.(\d)f\}/);
      var d=m?+m[1]:0;
      var s=v.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
      if(f.indexOf('$')===0)s='$'+s;
      if(f.indexOf('%')>-1)s=s+'%';
      return s;
    }
    function move(e){
      var r=svg.getBoundingClientRect();
      var vb=svg.viewBox.baseVal;
      var sx=(e.clientX-r.left)/r.width*vb.width;
      var rows='',label='',any=false;
      cfg.series.forEach(function(s,si){
        if(!s.pts.length){dots[si].style.display='none';return;}
        var best=s.pts[0],bd=1e9;
        s.pts.forEach(function(p){var d=Math.abs(p[0]-sx);if(d<bd){bd=d;best=p;}});
        dots[si].setAttribute('cx',best[0]);dots[si].setAttribute('cy',best[1]);
        dots[si].style.display='';
        label=best[2];any=true;
        rows+='<div class="r"><span class="sw" style="background:'+s.colour+'"></span>'+
              s.name+' <b>'+fmt(best[3])+'</b></div>';
        if(si===0)cross.setAttribute('x1',best[0]),cross.setAttribute('x2',best[0]);
      });
      if(!any)return;
      cross.style.display='';
      tip.innerHTML='<b>'+label+'</b>'+rows;
      tip.style.opacity='1';
      var px=(e.clientX-r.left), tw=tip.offsetWidth;
      tip.style.left=Math.max(4,Math.min(r.width-tw-4,px-tw/2))+'px';
      tip.style.top=Math.max(4,(e.clientY-r.top)-tip.offsetHeight-14)+'px';
    }
    function out(){
      cross.style.display='none';tip.style.opacity='0';
      dots.forEach(function(d){d.style.display='none';});
    }
    cap.addEventListener('mousemove',move);
    cap.addEventListener('mouseleave',out);
    cap.addEventListener('touchmove',function(e){if(e.touches[0])move(e.touches[0]);},{passive:true});
    cap.addEventListener('touchend',out);
  });
})();
"""

MARK = ('<svg width="18" height="18" viewBox="0 0 32 32" aria-hidden="true">'
        '<path d="M8 21l5-6 4 3 7-9" stroke="white" stroke-width="4" fill="none" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')

GH = "https://github.com/yennanliu/InvestSkill-test"
IS = "https://github.com/yennanliu/InvestSkill"

NAV_ITEMS = [
    ("index.html", "總覽"),
    ("screener.html", "四檔對決"),
    ("mu.html", "MU"),
    ("skhy.html", "SKHY"),
    ("mrvl.html", "MRVL"),
    ("sndl.html", "SNDL"),
    ("workflows.html", "工作流 A–G"),
    ("supply-chain.html", "產業鏈"),
]


CURRENT_ATTR = ' aria-current="page"'


def nav(active=""):
    links = "".join(
        f'<a href="{h}"{CURRENT_ATTR if h == active else ""}>{t}</a>'
        for h, t in NAV_ITEMS)
    return f"""<header class="nav"><div class="wrap nav__in">
<a class="brand" href="../index.html"><span class="brand__mark">{MARK}</span>
<span class="brand__text">InvestSkill Autopilot</span></a>
<nav class="nav__links" aria-label="展示頁面">{links}</nav>
<a class="btn btn--sm nav__cta" href="{GH}">
<span class="nav__cta-label">GitHub</span>
<svg width="17" height="17" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-2.92-.88-2.92-2.90 0-.86.31-1.57.82-2.12-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.81a5.4 5.4 0 0 1 2 0c1.53-1.04 2.2-.81 2.2-.81.44 1.1.16 1.92.08 2.12.51.55.82 1.25.82 2.12 0 2.03-1.15 2.70-2.93 2.90.3.26.56.76.56 1.54 0 1.11-.01 2.01-.01 2.29 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg></a>
</div><div class="prog" aria-hidden="true"><i></i></div></header>"""


def page(title, desc, body, active="", css_extra=""):
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#00b14f">
<meta name="robots" content="index,follow">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%2300b14f'/><path d='M8 21l5-6 4 3 7-9' stroke='white' stroke-width='3' fill='none' stroke-linecap='round' stroke-linejoin='round'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>{CSS}{css_extra}</style>
<script>document.documentElement.className="js"</script>
</head>
<body>
<a class="skip" href="#main">跳至主要內容</a>
{nav(active)}
<main id="main">
{body}
</main>
<a class="totop" href="#main" aria-label="回到頁首">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg></a>
<footer class="foot"><div class="wrap">
<p><strong>InvestSkill Autopilot — 展示櫃</strong>　·　由 <a href="{IS}">InvestSkill</a> v1.11.0（27 個分析框架）驅動，
報告內容由 LLM 依據 yfinance 公開資料生成。</p>
<p style="margin-top:8px">資料快照：2026-07-29　·　<a href="{GH}">原始碼與完整報告存檔</a>　·　<a href="../index.html">回專案首頁</a></p>
<div class="disc"><strong>免責聲明</strong>　本頁為技術與框架能力展示，並非投資建議。所有內容由大型語言模型依據免費公開資料自動生成，
可能存在錯誤、過時或內部不一致之處；文中已刻意保留並標示資料本身的缺陷（例如貨幣單位混用、上市歷史不足），
以示範 <code>result-validator</code> 框架的稽核能力。任何投資決策前請自行查證第一手文件（SEC EDGAR、公司投資人關係網站）。</div>
</div></footer>
<script>{JS}</script>
</body>
</html>"""


def toc(groups):
    """groups: [(group_label|None, [(anchor, label)])]"""
    h = '<aside class="toc" aria-label="本頁目錄"><div class="toc__h">本頁目錄</div>'
    for g, items in groups:
        if g: h += f'<div class="toc__grp">{g}</div>'
        for a, l in items:
            h += f'<a href="#{a}">{l}</a>'
    return h + "</aside>"
