document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on',x===b));
document.querySelectorAll('.view').forEach(v=>v.hidden=v.id!=='v-'+b.dataset.v);document.querySelectorAll('audio').forEach(a=>a.pause());sync();window.scrollTo(0,0)});
function sync(){document.querySelectorAll('.play').forEach(b=>{const a=document.getElementById('a-'+b.dataset.a);b.textContent=a.paused?'▶ Play':'❚❚ Pause'})}
document.querySelectorAll('.play').forEach(b=>{const a=document.getElementById('a-'+b.dataset.a),t=document.getElementById('t-'+b.dataset.a),total=t.textContent;
b.onclick=()=>{document.querySelectorAll('audio').forEach(x=>{if(x!==a)x.pause()});a.paused?a.play():a.pause()};
a.onplay=a.onpause=a.onended=sync;a.ontimeupdate=()=>{const s=a.currentTime|0;t.textContent=`${s/60|0}:${String(s%60).padStart(2,'0')} / ${total}`}});
