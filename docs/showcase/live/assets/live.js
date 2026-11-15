
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

(function(){
  /* archive filter: buttons narrow the cards to one ticker */
  var bar=document.querySelector('.lv-filter');
  if(bar){
    bar.hidden=false;
    bar.addEventListener('click',function(e){
      var b=e.target.closest('button'); if(!b) return;
      var want=b.getAttribute('data-t');
      bar.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
      document.querySelectorAll('.lv-card').forEach(function(c){
        c.hidden=!!want && c.getAttribute('data-t')!==want;});
      document.querySelectorAll('.lv-group').forEach(function(g){
        g.hidden=!g.querySelector('.lv-card:not([hidden])');});
    });
  }
  /* a showcase page learns its newer neighbour from the manifest, so an old
     page never has to be re-rendered when a new run is published */
  var pager=document.querySelector('.lv-pager[data-page]');
  if(pager && window.fetch){
    fetch('../runs.json').then(function(r){return r.json()}).then(function(m){
      var runs=m.runs||[], here=pager.getAttribute('data-page');
      for(var i=0;i<runs.length;i++){
        if(runs[i].page===here && i>0){
          var n=runs[i-1], a=pager.querySelector('.lv-newer');
          a.href='../'+n.page; a.textContent=n.date+' · '+n.ticker+' →'; a.hidden=false;
        }
      }
    }).catch(function(){});
  }
})();
