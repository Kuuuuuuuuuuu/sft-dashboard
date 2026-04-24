"""Jupyter 서버의 JSON 파일 → 자체 완결형 HTML → Jupyter에 업로드."""
import requests, json, re
from pathlib import Path

JUPYTER = "http://172.19.181.250:8888"
JUPYTER_PW = "mtdt2023"
TASK_IDS = ["G4-1", "G4-2", "G4-3", "G4-4", "G4-5", "G4-6"]
INDEX_HTML = Path(__file__).parent.parent / "index.html"

# 1. Jupyter 로그인
print("1. Jupyter 로그인...")
s = requests.Session()
r = s.get(f"{JUPYTER}/login")
xsrf = s.cookies.get("_xsrf", "")
s.post(f"{JUPYTER}/login", data={"_xsrf": xsrf, "password": JUPYTER_PW}, headers={"X-XSRFToken": xsrf})

# 2. Jupyter에서 JSON 파일 가져오기
print("2. JSON 파일 가져오기...")
TASKS = []
for tid in TASK_IDS:
    try:
        r = s.get(f"{JUPYTER}/api/contents/dashboard_data/summary_{tid}.json", headers={"X-XSRFToken": xsrf})
        if r.status_code == 200:
            content = r.json().get("content", "")
            t = json.loads(content)
            TASKS.append(t)
            print(f"   {tid} {t.get('name','')} | seeds:{len(t.get('seeds',[]))} samples:{len(t.get('samples',[]))}")
        else:
            print(f"   {tid}: 없음 ({r.status_code})")
    except Exception as e:
        print(f"   {tid}: 에러 ({e})")

print(f"   총 {len(TASKS)}개 태스크 로드")

# 3. HTML 생성
print("\n3. HTML 생성...")
html = INDEX_HTML.read_text("utf-8")

# JSON을 ASCII 이스케이프로 안전하게 변환
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

# SHEET_ID 비우기
html = re.sub(r"const SHEET_ID='[^']*';", "const SHEET_ID='';", html)

print(f"   {len(html)//1024}KB")

# 4. Jupyter에 업로드
print("\n4. Jupyter 업로드...")
r = s.put(f"{JUPYTER}/api/contents/sft_dashboard.html",
    json={"type": "file", "format": "text", "name": "sft_dashboard.html", "content": html},
    headers={"X-XSRFToken": xsrf})
print(f"   업로드: {r.status_code}")
print(f"\n   URL: {JUPYTER}/view/sft_dashboard.html")
