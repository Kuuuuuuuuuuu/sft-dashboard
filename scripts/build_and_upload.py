"""Jupyter 서버의 JSON 파일 → 자체 완결형 HTML → 노트북(.ipynb)으로 Jupyter에 업로드.
노트북 output에 HTML을 미리 넣어서 열자마자 바로 보임 (실행 불필요)."""
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

tasks_json = json.dumps(TASKS, ensure_ascii=True)
tasks_json = tasks_json.replace("</", "<\\/")

# load() 함수를 인라인 데이터 사용으로 교체
m = re.search(r"async function load\(\)\{.*?buildSb\(\);render\(\);\s*\}", html, re.DOTALL)
if m:
    html = html[:m.start()] + "async function load(){T=_D;buildSb();render();}" + html[m.end():]
    print("   load() 교체 완료")

# _D 데이터를 </script> 바로 앞에 삽입
html = html.replace("</script>", f"\nconst _D={tasks_json};\n</script>")

# SHEET_ID 제거
html = re.sub(r"const SHEET_ID='[^']*';\n?", "", html)

print(f"   {len(html)//1024}KB")

# 4. 노트북 생성 — output에 HTML을 미리 넣어서 실행 없이 바로 보임
print("\n4. 노트북 생성...")
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": [
        {
            "cell_type": "code",
            "metadata": {"jupyter": {"source_hidden": True}},
            "source": "from IPython.display import HTML\nHTML(open('sft_dashboard_embed.html','r',encoding='utf-8').read())",
            "outputs": [
                {
                    "output_type": "execute_result",
                    "data": {
                        "text/html": html
                    },
                    "metadata": {},
                    "execution_count": 1
                }
            ],
            "execution_count": 1
        }
    ]
}

# 5. 업로드
print("5. Jupyter 업로드...")

# HTML 파일도 업로드 (노트북에서 재실행 시 사용)
r = s.put(f"{JUPYTER}/api/contents/sft_dashboard_embed.html",
    json={"type": "file", "format": "text", "name": "sft_dashboard_embed.html", "content": html},
    headers={"X-XSRFToken": xsrf})
print(f"   HTML: {r.status_code}")

# 노트북 업로드
r = s.put(f"{JUPYTER}/api/contents/SFT_Dashboard.ipynb",
    json={"type": "notebook", "format": "json", "name": "SFT_Dashboard.ipynb", "content": notebook},
    headers={"X-XSRFToken": xsrf})
print(f"   노트북: {r.status_code}")

print(f"\n   URL: {JUPYTER}/notebooks/SFT_Dashboard.ipynb")
print("   (열면 바로 대시보드가 보입니다 — 실행 불필요)")
