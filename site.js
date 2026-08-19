const API='https://web-anaylsis.onrender.com';
const currentUser=()=>JSON.parse(localStorage.getItem('dailyGrindUser')||'null');
function requireLogin(){const u=currentUser();if(!u){location.href='auth.html?next='+encodeURIComponent(location.pathname);return null}return u}
function moneyINR(n){return '₹'+Number(n||0).toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2})}
function getCart(){return JSON.parse(localStorage.getItem('dailyGrindCart')||'[]')}
function saveCart(c){localStorage.setItem('dailyGrindCart',JSON.stringify(c));updateCartBadge()}
function updateCartBadge(){const c=getCart();const el=document.getElementById('cartCount');if(el)el.textContent=c.reduce((a,x)=>a+Number(x.quantity||0),0)}
async function syncUser(){const u=currentUser();if(!u)return null;try{const r=await fetch(`${API}/api/user/${u.user_id}`);if(r.ok){const d=await r.json();localStorage.setItem('dailyGrindUser',JSON.stringify(d.user));return d.user}}catch(e){}return u}
async function track(type,details={}){const u=currentUser();if(!u)return;const data={user_id:u.user_id,sessionId:sessionStorage.getItem('dgSession')||(Math.random().toString(36).slice(2)),pageVisited:location.pathname,device:navigator.userAgent,screenResolution:screen.width+'x'+screen.height,events:[{eventType:type,timestamp:Date.now(),...details}]};sessionStorage.setItem('dgSession',data.sessionId);try{await fetch(`${API}/api/track`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})}catch(e){}}
function updateAccountUI(){const u=currentUser();document.querySelectorAll('[data-account]').forEach(el=>{el.textContent=u?`Hi, ${u.name.split(' ')[0]} · ${u.credits} credits`:'Login / Sign up';el.href=u?'activity.html':'auth.html'});updateCartBadge()}
document.addEventListener('DOMContentLoaded',()=>{updateAccountUI();updateCartBadge()});
