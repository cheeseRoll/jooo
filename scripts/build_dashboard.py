"""Build docs/index.html — the self-contained job dashboard.

  python3 scripts/build_dashboard.py

Reads data/jobs.json; shows every non-expired job (scored ones ranked first).
"Applied" button opens a prefilled GitHub issue that the nightly session consumes.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOBS_DB = ROOT / "data" / "jobs.json"
OUT = ROOT / "docs" / "index.html"
REPO = "cheeseRoll/jooo"

FIELDS = ["id", "title", "company", "location", "url", "posted_at", "first_seen",
          "source", "salary", "stage", "status", "fit_score", "band", "geo_tag",
          "why", "resume_tips", "red_flags"]


def main():
    db = json.loads(JOBS_DB.read_text())
    jobs = [{**{k: j.get(k) for k in FIELDS},
             "applied_on": j.get("applied_on"), "mailed_on": j.get("mailed_on"),
             "desc": (j.get("description") or "")[:400]}
            for j in db["jobs"].values() if j.get("status") != "expired"]
    jobs.sort(key=lambda j: (-(j["fit_score"] or -1), j["posted_at"] or "", j["company"]))

    html = TEMPLATE.replace("__JOBS__", json.dumps(jobs, ensure_ascii=False)) \
                   .replace("__UPDATED__", date.today().isoformat()) \
                   .replace("__REPO__", REPO)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"dashboard: {len(jobs)} jobs → {OUT.relative_to(ROOT)}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Harsh — Job Board</title>
<style>
:root{
  --plane:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
  --line:#e1e0d9; --ring:rgba(11,11,11,.10); --accent:#2a78d6; --accent-ink:#1c5cab;
  --good:#0ca30c; --good-text:#006300; --warn:#fab219; --crit:#d03b3b;
}
@media (prefers-color-scheme: dark){:root{
  --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7; --muted:#898781;
  --line:#2c2c2a; --ring:rgba(255,255,255,.10); --accent:#3987e5; --accent-ink:#86b6ef;
  --good:#0ca30c; --good-text:#0ca30c;
}}
:root[data-theme=dark]{
  --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7; --muted:#898781;
  --line:#2c2c2a; --ring:rgba(255,255,255,.10); --accent:#3987e5; --accent-ink:#86b6ef;
  --good:#0ca30c; --good-text:#0ca30c;
}
:root[data-theme=light]{
  --plane:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
  --line:#e1e0d9; --ring:rgba(11,11,11,.10); --accent:#2a78d6; --accent-ink:#1c5cab;
  --good:#0ca30c; --good-text:#006300;
}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);
  font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:980px;margin:0 auto;padding:20px 14px 60px}
h1{font-size:22px;margin:6px 0 2px}
.sub{color:var(--muted);font-size:13px;margin-bottom:16px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:16px}
.tile{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:12px 14px}
.tile .v{font-size:26px;font-weight:650}
.tile .l{font-size:12px;color:var(--ink2)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;align-items:center}
.filters input,.filters select{background:var(--surface);color:var(--ink);
  border:1px solid var(--line);border-radius:8px;padding:7px 10px;font:inherit;font-size:13px}
.filters input{flex:1;min-width:140px}
label.tog{font-size:13px;color:var(--ink2);display:flex;gap:5px;align-items:center;cursor:pointer}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:12px;
  padding:14px 16px;margin-bottom:10px}
.row1{display:flex;gap:10px;align-items:flex-start;justify-content:space-between}
.jt{font-size:16px;font-weight:640;margin:0}
.co{color:var(--ink2);font-size:13.5px;margin:1px 0 6px}
.score{min-width:52px;text-align:center;border-radius:9px;padding:5px 8px 3px;
  font-weight:700;font-size:17px;border:1.5px solid var(--line);color:var(--ink2)}
.score small{display:block;font-size:9.5px;font-weight:600;letter-spacing:.04em}
.score.s80{border-color:var(--good);color:var(--good-text)}
.score.s65{border-color:var(--accent);color:var(--accent-ink)}
.score.s50{border-color:var(--warn);color:var(--ink2)}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin:2px 0 8px}
.b{font-size:11.5px;padding:2px 8px;border-radius:99px;border:1px solid var(--line);color:var(--ink2)}
.b.geo{border-color:var(--accent);color:var(--accent-ink)}
.b.visa{border-color:var(--good);color:var(--good-text)}
.b.flag{border-color:var(--crit);color:var(--crit)}
.why{font-size:13.5px;color:var(--ink2);margin:0 0 8px}
details{font-size:13px;color:var(--ink2);margin:6px 0}
summary{cursor:pointer;color:var(--accent-ink);font-size:12.5px}
.meta{font-size:12px;color:var(--muted);margin-bottom:8px}
.acts{display:flex;gap:8px;flex-wrap:wrap}
.btn{display:inline-block;text-decoration:none;font-size:13px;font-weight:600;
  padding:7px 14px;border-radius:8px;border:1px solid var(--line);color:var(--ink2)}
.btn.apply{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.done{border-color:var(--good);color:var(--good-text)}
.applied-tag{font-size:12px;color:var(--good-text);font-weight:650}
.empty{color:var(--muted);text-align:center;padding:40px 0}
</style></head><body>
<div class="wrap">
<h1>Harsh — Job Board</h1>
<div class="sub">Strategic finance @ Series B+ startups · Bengaluru &amp; abroad · updated __UPDATED__</div>
<div class="tiles" id="tiles"></div>
<div class="filters">
  <input id="q" placeholder="Search title / company…">
  <select id="geo"><option value="">All locations</option>
    <option value="BLR">Bengaluru</option>
    <option value="ABROAD+VISA">Abroad + visa</option>
    <option value="ABROAD?VISA">Abroad (visa unclear)</option></select>
  <select id="city"><option value="">All cities</option></select>
  <select id="band"><option value="">All scores</option>
    <option value="80">80+ apply today</option>
    <option value="65">65+ strong</option>
    <option value="50">50+</option></select>
  <select id="sort"><option value="fit">Sort: fit</option>
    <option value="date">Sort: newest</option></select>
  <label class="tog"><input type="checkbox" id="hideap" checked> hide applied</label>
</div>
<div id="list"></div>
</div>
<script>
const JOBS=__JOBS__;
const REPO="__REPO__";
const esc=s=>(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const days=d=>{if(!d)return null;return Math.round((Date.now()-new Date(d))/864e5)};
const ago=d=>{const n=days(d);return n==null?"":n<=0?"today":n+"d ago"};

// Optimistic status overlay: buttons take effect on this device instantly;
// the nightly rebuild bakes the real status in from the tracker afterwards.
const RANK={new:0,scored:0,applied:1,mailed:2};
const LS=JSON.parse(localStorage.getItem("jooo-status")||"{}");
function eff(j){
  const db=RANK[j.status]||0, loc=RANK[LS[j.id]]||0;
  return loc>db?LS[j.id]:j.status;}
function markLocal(id,st){
  LS[id]=st; localStorage.setItem("jooo-status",JSON.stringify(LS));
  setTimeout(render,150);}

function issueUrl(j,kind){
  const t=encodeURIComponent(kind+": "+j.id);
  const b=encodeURIComponent(j.company+" — "+j.title+"\n"+j.url);
  return `https://github.com/${REPO}/issues/new?title=${t}&body=${b}`;}

// city = first segment of location, with common aliases folded together
function cityOf(j){
  const l=(j.location||"").toLowerCase();
  if(/bengaluru|bangalore|\bblr\b/.test(l))return "Bengaluru";
  if(l.includes("singapore"))return "Singapore";
  if(l.includes("dubai"))return "Dubai";
  if(l.includes("abu dhabi"))return "Abu Dhabi";
  if(l.includes("london"))return "London";
  if(l.includes("new york"))return "New York";
  if(l.includes("san francisco"))return "San Francisco";
  const s=(j.location||"").split(",")[0].trim();
  return s?s.replace(/\b\w/g,c=>c.toUpperCase()):"Other";}
function card(j){
  const s=j.fit_score;
  const cls=s>=80?"s80":s>=65?"s65":s>=50?"s50":"";
  const lbl=s>=80?"apply now":s>=65?"strong":s>=50?"maybe":"fit";
  const badges=[];
  if(j.geo_tag)badges.push(`<span class="b ${j.geo_tag==="ABROAD+VISA"?"visa":"geo"}">${esc(j.geo_tag)}</span>`);
  if(j.stage)badges.push(`<span class="b">${esc(j.stage)}</span>`);
  if(j.location)badges.push(`<span class="b">${esc(j.location)}</span>`);
  if(j.salary)badges.push(`<span class="b">${esc(j.salary)}</span>`);
  if(j.red_flags)badges.push(`<span class="b flag">⚠ ${esc(j.red_flags)}</span>`);
  return `<div class="card">
  <div class="row1"><div>
    <p class="jt">${esc(j.title)}</p>
    <p class="co">${esc(j.company)}</p></div>
    <div class="score ${cls}">${s==null?"–":s}<small>${lbl}</small></div></div>
  <div class="badges">${badges.join("")}</div>
  ${j.why?`<p class="why">${esc(j.why)}</p>`:""}
  <div class="meta">posted ${j.posted_at?esc(j.posted_at)+" · "+ago(j.posted_at):"n/a"} · via ${esc(j.source)}</div>
  ${j.resume_tips?`<details><summary>Resume tweaks for this role</summary>${esc(j.resume_tips)}</details>`:""}
  ${j.desc?`<details><summary>Job description</summary>${esc(j.desc)}…</details>`:""}
  <div class="acts">
    <a class="btn apply" href="${esc(j.url)}" target="_blank" rel="noopener">Apply ↗</a>
    ${(()=>{const st=eff(j);
      if(st==="mailed")
        return `<span class="applied-tag">✓ applied · ✉ mailed${j.mailed_on?" "+esc(j.mailed_on):""}</span>`;
      if(st==="applied")
        return `<span class="applied-tag">✓ applied${j.applied_on?" "+esc(j.applied_on):""}</span>
          <a class="btn done" href="${issueUrl(j,"Mailed")}" target="_blank" rel="noopener"
             onclick="markLocal('${j.id}','mailed')">Cover mail sent ✉</a>`;
      return `<a class="btn done" href="${issueUrl(j,"Applied")}" target="_blank" rel="noopener"
             onclick="markLocal('${j.id}','applied')">Mark applied ✓</a>`;})()}
  </div></div>`;}
function tiles(list){
  const fresh=list.filter(j=>days(j.posted_at)!=null&&days(j.posted_at)<=7).length;
  const hot=list.filter(j=>j.fit_score>=80&&(RANK[eff(j)]||0)<1).length;
  const applied=JOBS.filter(j=>(RANK[eff(j)]||0)>=1).length;
  const mailed=JOBS.filter(j=>eff(j)==="mailed").length;
  document.getElementById("tiles").innerHTML=[
    [list.length,"open roles shown"],[hot,"scored 80+ (apply)"],
    [fresh,"posted ≤ 7 days"],[applied,`applied (${mailed} mailed)`]]
    .map(([v,l])=>`<div class="tile"><div class="v">${v}</div><div class="l">${l}</div></div>`).join("");}
function fillCities(){
  const counts={};
  for(const j of JOBS){const c=cityOf(j);counts[c]=(counts[c]||0)+1;}
  const cities=Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,18);
  const sel=document.getElementById("city");
  for(const [c,n] of cities){
    const o=document.createElement("option");
    o.value=c;o.textContent=`${c} (${n})`;sel.appendChild(o);}}
const roleKey=j=>j.company.toLowerCase()+"|"+j.title.toLowerCase().replace(/[^a-z0-9]/g,"");
function render(){
  const q=document.getElementById("q").value.toLowerCase();
  const geo=document.getElementById("geo").value;
  const city=document.getElementById("city").value;
  const band=+document.getElementById("band").value||0;
  const hide=document.getElementById("hideap").checked;
  const sort=document.getElementById("sort").value;
  // hide-applied hides the whole role (company+title), so duplicate listings of
  // a job he already applied to disappear too
  const appliedKeys=new Set(JOBS.filter(j=>(RANK[eff(j)]||0)>=1).map(roleKey));
  let list=JOBS.filter(j=>
    (!q||(j.title+" "+j.company+" "+j.location).toLowerCase().includes(q))
    &&(!geo||j.geo_tag===geo)&&(!city||cityOf(j)===city)
    &&(!band||(j.fit_score||0)>=band)
    &&(!hide||!appliedKeys.has(roleKey(j))));
  if(sort==="date")list=[...list].sort((a,b)=>(b.posted_at||"").localeCompare(a.posted_at||""));
  tiles(list);
  document.getElementById("list").innerHTML=
    list.length?list.map(card).join(""):`<div class="empty">Nothing matches — relax a filter.</div>`;}
for(const id of["q","geo","city","band","sort","hideap"])
  document.getElementById(id).addEventListener("input",render);
fillCities();
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
