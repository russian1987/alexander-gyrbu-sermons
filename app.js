let V=[],topic='Все',type='sermon';const $=s=>document.querySelector(s);
const fmtD=d=>d?`${d.slice(6,8)}.${d.slice(4,6)}.${d.slice(0,4)}`:'';
const fmtT=s=>{if(!s)return'';s=Math.round(s);const h=s/3600|0,m=(s%3600)/60|0,x=s%60;return(h?h+':'+String(m).padStart(2,'0'):m)+':'+String(x).padStart(2,'0')};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
fetch('videos.json').then(r=>r.json()).then(d=>{V=d;['q','sort'].forEach(i=>$('#'+i).addEventListener('input',render));
document.querySelectorAll('#type button').forEach(b=>b.onclick=()=>{type=b.dataset.t;document.querySelectorAll('#type button').forEach(x=>x.classList.toggle('on',x==b));render()});render()});
function render(){const q=$('#q').value.toLowerCase().trim();const base=V.filter(v=>type=='all'||v.type==type);
const c={};base.forEach(v=>v.topics.forEach(t=>c[t]=(c[t]||0)+1));const names=Object.keys(c).sort((a,b)=>(a=='Другое')-(b=='Другое')||c[b]-c[a]);
if(topic!='Все'&&!c[topic])topic='Все';
$('#topics').innerHTML=[['Все',base.length],...names.map(n=>[n,c[n]])].map(([n,k])=>`<button class="${n==topic?'on':''}" data-n="${esc(n)}"><span>${esc(n)}</span><small>${k}</small></button>`).join('');
document.querySelectorAll('#topics button').forEach(b=>b.onclick=()=>{topic=b.dataset.n;render()});
let L=base.filter(v=>(topic=='Все'||v.topics.includes(topic))&&(!q||(v.title+' '+v.channel).toLowerCase().includes(q)));
const s=$('#sort').value;L.sort(s=='new'?(a,b)=>(b.date||'').localeCompare(a.date||''):s=='old'?(a,b)=>(a.date||'9').localeCompare(b.date||'9'):s=='long'?(a,b)=>(b.duration||0)-(a.duration||0):(a,b)=>(b.views||0)-(a.views||0));
$('#count').textContent=`Видео: ${L.length}`;
$('#grid').innerHTML=L.map(v=>`<article class="card"><button class="thumb" data-id="${v.id}" aria-label="Смотреть"><img loading="lazy" src="${v.thumb}" alt=""><span class="dur">${fmtT(v.duration)}</span></button>
<div class="body"><a href="https://www.youtube.com/watch?v=${v.id}" target="_blank" rel="noopener">${esc(v.title)}</a><div class="meta">${esc(v.channel||'')}${v.date?' · '+fmtD(v.date):''}</div><div class="tags">${v.topics.map(t=>`<span>${esc(t)}</span>`).join('')}</div></div></article>`).join('');
document.querySelectorAll('.thumb').forEach(b=>b.onclick=()=>{b.innerHTML=`<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.id}?autoplay=1" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;b.onclick=null})}
