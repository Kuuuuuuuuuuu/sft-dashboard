"""Jupyter 서버에 대시보드 업로드."""
import requests
import json
from pathlib import Path

SERVER = "http://172.19.181.250:8888"
PASSWORD = "mtdt2023"
HTML_FILE = Path(__file__).parent.parent / "index.html"

s = requests.Session()

# 로그인
r = s.get(f"{SERVER}/login")
xsrf = s.cookies.get("_xsrf", "")
s.post(f"{SERVER}/login", data={"_xsrf": xsrf, "password": PASSWORD}, headers={"X-XSRFToken": xsrf})
print("로그인 완료")

html = HTML_FILE.read_text("utf-8")

# HTML 파일 업로드
r = s.put(f"{SERVER}/api/contents/sft_dashboard.html",
    json={"type": "file", "format": "text", "name": "sft_dashboard.html", "content": html},
    headers={"X-XSRFToken": xsrf})
print(f"HTML 업로드: {r.status_code}")

# 노트북 생성 — 자동 실행 + 코드 숨김
notebook = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "celltoolbar": "Tags"
    },
    "cells": [
        {
            "cell_type": "code",
            "metadata": {"tags": ["hide-input"], "jupyter": {"source_hidden": True}},
            "source": "# 자동 실행 설정\nimport IPython\nIPython.get_ipython().run_cell_magic('javascript', '', 'Jupyter.notebook.execute_all_cells()')",
            "outputs": [],
            "execution_count": None
        },
        {
            "cell_type": "code",
            "metadata": {"tags": ["hide-input"], "jupyter": {"source_hidden": True}},
            "source": 'from IPython.display import HTML\nHTML(open("sft_dashboard.html","r",encoding="utf-8").read())',
            "outputs": [],
            "execution_count": None
        }
    ]
}

r = s.put(f"{SERVER}/api/contents/SFT_Dashboard.ipynb",
    json={"type": "notebook", "format": "json", "name": "SFT_Dashboard.ipynb", "content": notebook},
    headers={"X-XSRFToken": xsrf})
print(f"노트북 업로드: {r.status_code}")
print(f"\nVoila URL: {SERVER}/voila/render/SFT_Dashboard.ipynb")
print(f"노트북 URL: {SERVER}/notebooks/SFT_Dashboard.ipynb")
