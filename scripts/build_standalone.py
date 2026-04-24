"""Google Sheets 데이터를 가져와서 자체 완결형 HTML 생성 + Jupyter 업로드."""
import requests
import json
import csv
import io
from pathlib import Path

SHEET_ID = "1y6OEISDUfad_NaM7Jx0kYNaxk5fSVOHUK_LVIIiEYXw"
TASK_IDS = ["G4-1", "G4-2", "G4-3", "G4-4", "G4-5", "G4-6"]
INDEX_HTML = Path(__file__).parent.parent / "index.html"
OUT_HTML = Path(__file__).parent.parent / "sft_dashboard_standalone.html"
JUPYTER = "http://172.19.181.250:8888"
JUPYTER_PW = "mtdt2023"

def fetch_csv(tab):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab}"
    r = requests.get(url, timeout=30)
    return list(csv.DictReader(io.StringIO(r.text)))

def plang(s):
    import re
    m = re.match(r".*?(\d+)\s*:\s*(\d+)", s or "")
    if not m: return {}
    return {"EN": int(m.group(1)), "KO": int(m.group(2))} if "EN:KO" in (s or "") else {"KO": int(m.group(1)), "EN": int(m.group(2))}

def pcot(s):
    import re
    t = re.search(r"think\s*(\d+)", s or "", re.I)
    n = re.search(r"no_think\s*(\d+)", s or "", re.I)
    return {"think": int(t.group(1)) if t else 0, "no_think": int(n.group(1)) if n else 0}

print("1. Google Sheets에서 데이터 가져오기...")
tR = fetch_csv("tasks")
sR = fetch_csv("seeds")
pR = fetch_csv("pipeline")
iR = fetch_csv("issues")
dR = fetch_csv("crossDims")
tdR = fetch_csv("turnDist")

tdM = {}
for r in tdR:
    tid, dn = r["task_id"], r["dim_name"]
    tdM.setdefault(tid, {}).setdefault(dn, {})[r["turns"]] = int(r["count"] or 0)

# JSON에서 samples + prompts
sm, pm = {}, {}
data_dir = Path(__file__).parent.parent / "data"
for tid in TASK_IDS:
    fp = data_dir / f"summary_{tid}.json"
    if fp.exists():
        d = json.loads(fp.read_text("utf-8"))
        if d.get("samples"): sm[tid] = d["samples"]
        if d.get("prompts"): pm[tid] = d["prompts"]

dedup = lambda a, k: list({x[k]: x for x in a}.values())

TASKS = []
for r in tR:
    if r["id"] not in TASK_IDS: continue
    tid = r["id"]
    TASKS.append({
        "id": tid, "name": r.get("name", ""), "desc": r.get("desc", ""), "status": r.get("status", "wait"),
        "info": {"tier": int(r.get("tier") or 0), "target": int(r.get("target") or 0), "minimum": int(r.get("minimum") or 0),
                 "lang_ratio": r.get("lang_ratio", ""), "cot_ratio": r.get("cot_ratio", "")},
        "seeds": dedup([{"name": s["name"], "category": s["category"], "usage": s["usage"],
                         "contamination": s.get("contamination", "-"), "count": int(s.get("count") or 0)}
                        for s in sR if s["task_id"] == tid], "name"),
        "crossDims": [{"name": x["name"], "target": int(x.get("target") or 0), "actual": int(x.get("actual") or 0),
                        "turnDist": tdM.get(tid, {}).get(x["name"], {})} for x in dR if x["task_id"] == tid],
        "dataStats": {"completed": int(r.get("completed") or 0), "pass_rate": float(r.get("pass_rate") or 0),
                      "avg_turns": float(r.get("avg_turns") or 0), "lang": plang(r.get("lang_ratio", "")),
                      "cot": pcot(r.get("cot_ratio", "")), "domains": []},
        "pipeline": dedup([{"phase": p["phase"], "name": p["name"], "detail": p.get("detail", ""), "status": p.get("status", "wait")}
                           for p in pR if p["task_id"] == tid], "phase"),
        "issues": [{"severity": i.get("severity", "info"), "text": i.get("text", ""), "date": i.get("date", "")}
                   for i in iR if i["task_id"] == tid],
        "prompts": pm.get(tid, {}),
        "samples": sm.get(tid, [])
    })

for t in TASKS:
    print(f'  {t["id"]} {t["name"]} | seeds:{len(t["seeds"])} pipe:{len(t["pipeline"])} samples:{len(t["samples"])}')

print(f"\n2. 자체 완결형 HTML 생성...")
html = INDEX_HTML.read_text("utf-8")

# SHEET_ID를 비우고 inline TASKS 삽입
tasks_json = json.dumps(TASKS, ensure_ascii=False)
html = html.replace(
    "const SHEET_ID='1y6OEISDUfad_NaM7Jx0kYNaxk5fSVOHUK_LVIIiEYXw';",
    "const SHEET_ID='';"
)

# loadFromJSON을 inline data로 교체
old_load = "async function loadFromJSON(){"
new_load = f"const _INLINE=true;const _TASKS_DATA={tasks_json};\nasync function loadFromJSON(){{"
html = html.replace(old_load, new_load)

# fetch 대신 inline data 사용
old_fetch = """const r=await Promise.allSettled(TASK_IDS.map(id=>fetch('data/summary_'+id+'.json').then(r=>{if(!r.ok)throw 0;return r.json();})));
  r.forEach(x=>{if(x.status==='fulfilled')TASKS.push(x.value);});"""
new_fetch = "_TASKS_DATA.forEach(t=>TASKS.push(t));"
html = html.replace(old_fetch, new_fetch)

# samples fetch도 제거 (이미 inline에 포함)
old_samples = """const sm={},pm={};
    for(const id of TASK_IDS){try{const r=await fetch('data/summary_'+id+'.json?t='+Date.now());if(r.ok){const d=await r.json();if(d?.samples?.length)sm[id]=d.samples;if(d?.prompts)pm[id]=d.prompts;}}catch(e){}}"""
new_samples = "const sm={},pm={};"
html = html.replace(old_samples, new_samples)

# prompts와 samples를 TASKS에 이미 포함
old_build = "      prompts:pm[id]||{},"
new_build = "      prompts:pm[id]||t_inline?.prompts||{}," if False else "      prompts:pm[id]||{},"

OUT_HTML.write_text(html, "utf-8")
print(f"  저장: {OUT_HTML} ({len(html)//1024}KB)")

print(f"\n3. Jupyter 서버에 업로드...")
s = requests.Session()
r = s.get(f"{JUPYTER}/login")
xsrf = s.cookies.get("_xsrf", "")
s.post(f"{JUPYTER}/login", data={"_xsrf": xsrf, "password": JUPYTER_PW}, headers={"X-XSRFToken": xsrf})

r = s.put(f"{JUPYTER}/api/contents/sft_dashboard.html",
    json={"type": "file", "format": "text", "name": "sft_dashboard.html", "content": html},
    headers={"X-XSRFToken": xsrf})
print(f"  업로드: {r.status_code}")
print(f"\n  URL: {JUPYTER}/view/sft_dashboard.html")
