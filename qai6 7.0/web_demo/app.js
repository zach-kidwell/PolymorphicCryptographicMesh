const algorithms = {
  "RSA-2048": { risk: "High quantum risk", confidence: 98, reason: "Shor's algorithm can factor RSA keys efficiently.", high: true },
  "ECC-256": { risk: "High quantum risk", confidence: 97, reason: "A large quantum computer could solve its discrete logarithm.", high: true },
  "AES-256": { risk: "Low quantum risk", confidence: 91, reason: "Its larger key size retains a strong margin against Grover search.", high: false },
  "Kyber": { risk: "Quantum-resistant", confidence: 94, reason: "A lattice-based NIST standard designed for key establishment.", high: false },
  "Dilithium": { risk: "Quantum-resistant", confidence: 93, reason: "A lattice-based NIST standard designed for signatures.", high: false },
  "SPHINCS+": { risk: "Quantum-resistant", confidence: 92, reason: "A stateless hash-based signature design.", high: false }
};

const nodes = [
  {x:.09,y:.69,label:"A"},{x:.25,y:.39,label:"B"},{x:.31,y:.79,label:"C"},{x:.48,y:.56,label:"D"},
  {x:.59,y:.25,label:"E"},{x:.68,y:.72,label:"F"},{x:.83,y:.48,label:"G"},{x:.92,y:.20,label:"H"}
];
const edges = [[0,1,4],[0,2,6],[1,2,3],[1,3,5],[1,4,8],[2,3,2],[2,5,7],[3,4,4],[3,5,3],[3,6,6],[4,6,2],[4,7,6],[5,6,4],[6,7,3]];
const highRoute = [0,1,3,4,6,7];
const lowRoute = [0,1,4,7];
let route = highRoute;
let running = false;
let activeProgress = -1;
let currentHop = -1;

const canvas = document.querySelector("#networkCanvas");
const ctx = canvas.getContext("2d");
const packet = document.querySelector("#packet");
const algorithm = document.querySelector("#algorithm");
const message = document.querySelector("#message");
const sendButton = document.querySelector("#sendButton");

function sizeCanvas() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr; canvas.height = rect.height * dpr;
  ctx.setTransform(dpr,0,0,dpr,0,0);
  drawNetwork();
}

function point(n) { return {x:n.x*canvas.clientWidth,y:n.y*canvas.clientHeight}; }
function onRoute(a,b) { return route.some((n,i)=> i < route.length-1 && ((n===a && route[i+1]===b)||(n===b && route[i+1]===a))); }

function drawNetwork() {
  const w=canvas.clientWidth,h=canvas.clientHeight; ctx.clearRect(0,0,w,h);
  edges.forEach(([a,b,cost])=>{
    const p=point(nodes[a]),q=point(nodes[b]); const selected=running && onRoute(a,b);
    ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y);
    ctx.strokeStyle=selected ? "rgba(185,238,92,.82)" : "rgba(125,183,166,.28)";
    ctx.lineWidth=selected ? 2.4 : 1; if(selected){ctx.shadowColor="#b9ee5c";ctx.shadowBlur=8;} ctx.stroke(); ctx.shadowBlur=0;
    const mx=(p.x+q.x)/2,my=(p.y+q.y)/2; ctx.fillStyle="rgba(176,207,197,.44)";ctx.font="8px ui-monospace,monospace";ctx.fillText(cost,mx+4,my-4);
  });
  nodes.forEach((n,i)=>{
    const p=point(n),selected=running && route.includes(i); ctx.beginPath();ctx.arc(p.x,p.y,selected?9:7,0,Math.PI*2);
    ctx.fillStyle=selected?"#b9ee5c":"#62a994"; ctx.shadowColor=selected?"#b9ee5c":"transparent";ctx.shadowBlur=selected?13:0;ctx.fill();ctx.shadowBlur=0;
    ctx.beginPath();ctx.arc(p.x,p.y,selected?3.5:2.5,0,Math.PI*2);ctx.fillStyle="#0c2922";ctx.fill();
    ctx.fillStyle=selected?"#e8f7c9":"#92b7ac";ctx.font="700 9px ui-monospace,monospace";ctx.fillText(n.label,p.x+11,p.y+3);
  });
}

function setRisk() {
  const data=algorithms[algorithm.value], card=document.querySelector("#riskCard");
  card.classList.toggle("low",!data.high); document.querySelector("#riskLabel").textContent=data.risk;
  document.querySelector("#riskReason").textContent=data.reason; document.querySelector("#confidence").textContent=data.confidence+"%";
  document.querySelector(".risk-icon").textContent=data.high?"!":"✓";
}

function updatePacket(progress) {
  const segments=route.length-1,scaled=Math.min(progress, .999)*segments,index=Math.floor(scaled),t=scaled-index;
  const a=point(nodes[route[index]]),b=point(nodes[route[Math.min(index+1,segments)]]);
  packet.style.left=(a.x+(b.x-a.x)*t)+"px";packet.style.top=(a.y+(b.y-a.y)*t)+"px";
}

function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
function explainAction(title, detail, pulse=false){
  const note=document.querySelector("#hopNote");
  note.querySelector("strong").textContent=title;note.querySelector("span").textContent=detail;
  note.classList.toggle("pulse",pulse);
}
async function runSimulation(){
  if(running)return; running=true; const data=algorithms[algorithm.value];route=data.high?highRoute:lowRoute;
  sendButton.disabled=true;sendButton.querySelector("span").textContent="Classifying threat…";
  document.querySelector("#statusValue").textContent="Analyzing";document.querySelector("#modePill").classList.add("active");
  document.querySelector("#modePill").innerHTML="<i></i> AI threat scan";document.querySelector("#networkSubtitle").textContent="The classifier is evaluating the selected algorithm.";
  explainAction("1 · Assess the algorithm",`${algorithm.value} is checked against known quantum attack methods.`);
  drawNetwork();await sleep(700);
  sendButton.querySelector("span").textContent="Optimizing route…";document.querySelector("#modePill").innerHTML=data.high?"<i></i> Polymorphic mesh active":"<i></i> Classical secure channel";
  document.querySelector("#networkSubtitle").textContent=data.high?"High risk detected — activating extra layers of protection.":"Lower risk detected — the simple secure channel is sufficient.";
  explainAction(data.high?"2 · Activate layered defense":"2 · Keep the simple channel",data.high?"The message will use several relays and a different key at every hop.":"Extra relays would add complexity without improving this simulation's risk response.",true);
  drawNetwork();await sleep(650);
  document.querySelector("#routeValue").textContent=data.high?"Mesh + rotating keys":"Direct secure channel";
  document.querySelector("#latencyValue").textContent=data.high?"18.4 ms":"11.2 ms";
  document.querySelector("#mutationsValue").textContent=data.high?(route.length-1)+" fresh keys":"0 · stable key";
  document.querySelector("#statusValue").textContent="In transit";sendButton.querySelector("span").textContent="Transmitting…";
  packet.classList.add("visible");
  const start=performance.now(), duration=data.high?2600:1900;currentHop=-1;
  await new Promise(resolve=>{function frame(now){const p=Math.min((now-start)/duration,1);updatePacket(p);const hop=Math.min(Math.floor(p*(route.length-1)),route.length-2);if(hop!==currentHop){currentHop=hop;const from=nodes[route[hop]].label,to=nodes[route[hop+1]].label;explainAction(data.high?`3 · Key mutation ${hop+1} of ${route.length-1}`:"3 · Protected delivery",data.high?`Relay ${from} passes to ${to}. Fresh quantum-style entropy mutates the key.`:`The protected message moves from Alice to Bob through the efficient channel.`,true);}if(p<1)requestAnimationFrame(frame);else resolve();}requestAnimationFrame(frame);});
  document.querySelector("#statusValue").textContent="Delivered";document.querySelector("#networkSubtitle").textContent="Message recovered successfully at the destination.";
  explainAction("Message delivered",data.high?`Bob reverses ${route.length-1} key mutations and recovers Alice's original message.`:"Bob decrypts and recovers Alice's original message.");
  sendButton.querySelector("span").textContent="Transmission complete ✓";await sleep(700);packet.classList.remove("visible");
  sendButton.disabled=false;sendButton.querySelector("span").textContent="Run another transmission";running=false;
}

algorithm.addEventListener("change",setRisk);sendButton.addEventListener("click",runSimulation);
message.addEventListener("input",()=>document.querySelector("#charCount").textContent=`${message.value.length} / 80`);
const dialog=document.querySelector("#lessonDialog");
document.querySelector("#openLesson").addEventListener("click",()=>dialog.showModal());document.querySelector("#aboutButton").addEventListener("click",()=>dialog.showModal());document.querySelector("#closeDialog").addEventListener("click",()=>dialog.close());
window.addEventListener("resize",sizeCanvas);new ResizeObserver(sizeCanvas).observe(document.querySelector("#networkStage"));setRisk();sizeCanvas();
