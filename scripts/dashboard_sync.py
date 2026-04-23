#!/usr/bin/env python3
"""
파이프라인 결과 → Google Sheets 자동 동기화.

사용법:
    # 파이프라인 코드 끝에 추가
    from dashboard_sync import sync
    sync("G4-1", summary_dict)

    # 또는 CLI로 실행
    python dashboard_sync.py G4-1 result/summary.json

환경변수:
    DASHBOARD_WEBHOOK_URL  — Google Apps Script 웹앱 URL (필수)
"""

import json
import sys
import urllib.request
import urllib.error
import os
from pathlib import Path
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  설정
# ══════════════════════════════════════════════════════════════
WEBHOOK_URL = os.environ.get("https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec", "")
RETRY = 2
TIMEOUT = 30


def sync(task_id: str, summary: dict, webhook_url: str = ""):
    """summary dict를 Google Sheets로 전송."""
    url = webhook_url or WEBHOOK_URL
    if not url:
        print("[dashboard_sync] DASHBOARD_WEBHOOK_URL 미설정, 건너뜀")
        return False

    summary["id"] = task_id
    summary["_synced_at"] = datetime.now().isoformat()

    payload = json.dumps(summary, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(1, RETRY + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                body = resp.read().decode()
                print(f"[dashboard_sync] {task_id} 동기화 완료 ({resp.status})")
                return True
        except urllib.error.URLError as e:
            print(f"[dashboard_sync] 시도 {attempt}/{RETRY} 실패: {e}")
        except Exception as e:
            print(f"[dashboard_sync] 오류: {e}")

    print("[dashboard_sync] 동기화 실패 — 대시보드 수동 업데이트 필요")
    return False


def sync_from_file(task_id: str, filepath: str, webhook_url: str = ""):
    """JSON 파일에서 summary를 읽어 전송."""
    data = json.loads(Path(filepath).read_text("utf-8"))
    return sync(task_id, data, webhook_url)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python dashboard_sync.py <TASK_ID> <SUMMARY_JSON_PATH>")
        print("  예: python dashboard_sync.py G4-1 result/summary.json")
        sys.exit(1)

    tid = sys.argv[1]
    path = sys.argv[2]
    url = sys.argv[3] if len(sys.argv) > 3 else ""
    ok = sync_from_file(tid, path, url)
    sys.exit(0 if ok else 1)
