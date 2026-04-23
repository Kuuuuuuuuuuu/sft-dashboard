#!/usr/bin/env python3
"""
전체 태스크 일괄 동기화.

사용법:
    python scripts/sync_all.py                # reset + 전체 동기화
    python scripts/sync_all.py --no-reset     # reset 없이 동기화만
    python scripts/sync_all.py --reset-only   # reset만 (데이터 비우기)
"""

import json
import sys
import urllib.request
from pathlib import Path

WEBHOOK = (
    "https://script.google.com/macros/s/"
    "AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"
)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TIMEOUT = 60


def post(payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK, data=data, headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=TIMEOUT)
    return json.loads(resp.read().decode("utf-8"))


def reset():
    print("[reset] 모든 탭 초기화 중...")
    result = post({"_action": "reset"})
    print(f"[reset] {result}")


def sync_bulk():
    files = sorted(DATA_DIR.glob("summary_G4-*.json"))
    if not files:
        print(f"[error] {DATA_DIR} 에 summary_G4-*.json 파일 없음")
        sys.exit(1)

    tasks = []
    for f in files:
        task = json.loads(f.read_text("utf-8"))
        tasks.append(task)
        print(f"  로드: {f.name} ({task['id']})")

    print(f"\n[bulk] {len(tasks)}개 태스크 일괄 전송 중...")
    result = post({"_action": "bulk", "tasks": tasks})
    print(f"[bulk] {json.dumps(result, ensure_ascii=False, indent=2)}")


def main():
    args = set(sys.argv[1:])

    if "--reset-only" in args:
        reset()
        return

    if "--no-reset" not in args:
        reset()

    sync_bulk()
    print("\n완료.")


if __name__ == "__main__":
    main()
