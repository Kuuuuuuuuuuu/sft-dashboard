"""GitHub Pages HTML + Sheets 데이터 → 자체 완결형 HTML → Jupyter 업로드."""
import requests, json, csv, io, re
from pathlib import Path

SHEET_ID = "1y6OEISDUfad_NaM7Jx0kYNaxk5fSVOHUK_LVIIiEYXw"
TASK_IDS = ["G4-1", "G4-2", "G4-3", "G4-4", "G4-5", "G4-6"]
INDEX_HTML = Path(__file__).parent.parent / "index.html"
JUPYTER = "http://172.19.181.250:8888"
JUPYTER_PW = "mtdt2023"

def fetch_csv(tab):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab}"
    return list(csv.DictReader(io.StringIO(requests.get(url, timeout=30).text)))

def plang(s):
    m = re.match(r".*?(\d+)\s*:\s*(\d+)", s or "")
    if not m: return {}
    return {"EN": int(m.group(1)), "KO": int(m.group(2))} if "EN:KO" in (s or "") else {}

def pcot(s):
    t = re.search(r"think\s*(\d+)", s or "", re.I)
    n = re.search(r"no_think\s*(\d+)", s or "", re.I)
    return {"think": int(t.group(1)) if t else 0, "no_think": int(n.group(1)) if n else 0}

# 1. Sheets 데이터
print("1. Sheets 데이터...")
tR = fetch_csv("tasks")
sR = fetch_csv("seeds")
pR = fetch_csv("pipeline")
iR = fetch_csv("issues")
dR = fetch_csv("crossDims")
tdR = fetch_csv("turnDist")

# turnDist 매핑
tdM = {}
for r in tdR:
    tid, dn = r["task_id"], r["dim_name"]
    tdM.setdefault(tid, {}).setdefault(dn, {})[r["turns"]] = int(r["count"] or 0)

print(f"   turnDist 항목: {sum(len(v) for v in tdM.values())}개")
for tid, dims in tdM.items():
    for dn, td in dims.items():
        print(f"   {tid} {dn}: {td}")

# 2. JSON에서 samples, prompts
data_dir = Path(__file__).parent.parent / "data"
sm, pm = {}, {}
for tid in TASK_IDS:
    fp = data_dir / f"summary_{tid}.json"
    if fp.exists():
        try:
            d = json.loads(fp.read_text("utf-8"))
            if d.get("samples"): sm[tid] = d["samples"]
            if d.get("prompts"): pm[tid] = d["prompts"]
        except: pass

# 3. TASKS 빌드
dedup = lambda a, k: list({x[k]: x for x in a}.values())
TASKS = []
for r in tR:
    if r["id"] not in TASK_IDS: continue
    tid = r["id"]

    # crossDims에 turnDist 정확히 매핑
    cross_dims = []
    for x in dR:
        if x["task_id"] != tid: continue
        td = tdM.get(tid, {}).get(x["name"], {})
        cross_dims.append({
            "name": x["name"],
            "target": int(x.get("target") or 0),
            "actual": int(x.get("actual") or 0),
            "turnDist": td
        })

    TASKS.append({
        "id": tid, "name": r.get("name", ""), "desc": r.get("desc", ""), "status": r.get("status", "wait"),
        "info": {"tier": int(r.get("tier") or 0), "target": int(r.get("target") or 0),
                 "minimum": int(r.get("minimum") or 0), "lang_ratio": r.get("lang_ratio", ""),
                 "cot_ratio": r.get("cot_ratio", "")},
        "seeds": dedup([{"name": s["name"], "category": s["category"], "usage": s["usage"],
                         "contamination": s.get("contamination", "-"), "count": int(s.get("count") or 0)}
                        for s in sR if s["task_id"] == tid], "name"),
        "crossDims": cross_dims,
        "dataStats": {"completed": int(r.get("completed") or 0), "pass_rate": float(r.get("pass_rate") or 0),
                      "avg_turns": float(r.get("avg_turns") or 0), "lang": plang(r.get("lang_ratio", "")),
                      "cot": pcot(r.get("cot_ratio", "")), "domains": []},
        "pipeline": dedup([{"phase": p["phase"], "name": p["name"], "detail": p.get("detail", ""),
                           "status": p.get("status", "wait")} for p in pR if p["task_id"] == tid], "phase"),
        "issues": [{"severity": i.get("severity", "info"), "text": i.get("text", ""), "date": i.get("date", "")}
                   for i in iR if i["task_id"] == tid],
        "prompts": pm.get(tid, {}),
        "samples": sm.get(tid, [])
    })

for t in TASKS:
    has_td = any(d["turnDist"] for d in t["crossDims"])
    print(f'   {t["id"]} {t["name"]} | seeds:{len(t["seeds"])} samples:{len(t["samples"])} turnDist:{has_td}')

# 4. HTML 생성
print("\n2. HTML 생성...")
html = INDEX_HTML.read_text("utf-8")

# JSON을 HTML-safe하게: ensure_ascii=True로 한글을 \uXXXX로 이스케이프
tasks_json = json.dumps(TASKS, ensure_ascii=True)
tasks_json = tasks_json.replace("</", "<\\/")

new_load = f"""
const _D={tasks_json};
async function load(){{T=_D;buildSb();render();}}
"""

m = re.search(r"async function load\(\)\{.*?buildSb\(\);render\(\);\s*\}", html, re.DOTALL)
if m:
    html = html[:m.start()] + new_load + html[m.end():]
    print("   load() 교체 완료")
else:
    print("   load() 못 찾음!")
html = html.replace("const SHEET_ID='1y6OEISDUfad_NaM7Jx0kYNaxk5fSVOHUK_LVIIiEYXw';", "const SHEET_ID='';")

print(f"   {len(html)//1024}KB")

# 5. Jupyter 업로드
print("\n3. Jupyter 업로드...")
s = requests.Session()
r = s.get(f"{JUPYTER}/login")
xsrf = s.cookies.get("_xsrf", "")
s.post(f"{JUPYTER}/login", data={"_xsrf": xsrf, "password": JUPYTER_PW}, headers={"X-XSRFToken": xsrf})

r = s.put(f"{JUPYTER}/api/contents/sft_dashboard.html",
    json={"type": "file", "format": "text", "name": "sft_dashboard.html", "content": html},
    headers={"X-XSRFToken": xsrf})
print(f"   업로드: {r.status_code}")
print(f"\n   URL: {JUPYTER}/view/sft_dashboard.html")
