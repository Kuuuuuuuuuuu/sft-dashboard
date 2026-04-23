#!/usr/bin/env python3
"""
SFT 데이터 구축 파이프라인 템플릿.

사용법:
    1. 이 파일을 복사하여 본인 프로젝트에 넣기
    2. ═══ 설정 ═══ 섹션의 값 수정
    3. ═══ 파이프라인 구현 ═══ 섹션에 본인 로직 작성
    4. python pipeline_template.py 실행

    나머지(결과 집계, 대시보드 동기화)는 자동으로 처리됩니다.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
#  설정 — 본인 태스크에 맞게 수정
# ═══════════════════════════════════════════════════════════════
TASK_ID = "G4-1"                    # ← 본인 태스크 번호
TASK_NAME = "도메인 전문가 롤플레이"  # ← 태스크 이름
TASK_DESC = "30개 도메인 전문가 페르소나 기반 전문 상담 대화"
TASK_STATUS = "wip"                 # done / wip / wait

TIER = 2
TARGET = 3500
MINIMUM = 1000
LANG_RATIO = "EN:KO = 5:5"
COT_RATIO = "think 30% / no_think 70%"

RESULT_DIR = Path("result")         # ← 결과 파일 경로
RESULT_DIR.mkdir(exist_ok=True)

# 시드 데이터 정보
SEEDS = [
    {"name": "시드 이름", "category": "D (Synthetic)", "usage": "사용 방식 설명", "contamination": "-"},
]

# 횡단차원 (없으면 빈 리스트)
CROSS_DIMS = [
    # {"name": "차원명", "target": 40, "actual": 0, "turnDist": {}},
]

# ═══════════════════════════════════════════════════════════════
#  파이프라인 구현 — 본인 로직 작성
# ═══════════════════════════════════════════════════════════════

def build_seeds():
    """Phase 1: 시드 구축. 시드 데이터를 생성/로드."""
    print("[Phase 1] 시드 구축")
    # TODO: 본인 시드 구축 로직
    pass

def validate_seeds():
    """Phase 2: 시드 검증. 시드 품질 확인."""
    print("[Phase 2] 시드 검증")
    # TODO: 본인 시드 검증 로직
    pass

def generate_dialogues():
    """Phase 3: 대화 생성. 메인 생성 로직."""
    print("[Phase 3] 대화 생성")
    # TODO: 본인 대화 생성 로직
    # 결과를 RESULT_DIR 에 저장
    pass

def validate_quality():
    """Phase 4: 품질 검증."""
    print("[Phase 4] 품질 검증")
    # TODO: 본인 품질 검증 로직
    pass

def get_pipeline_status():
    """각 Phase의 현재 상태를 반환. 본인 판단 기준으로 수정."""
    # TODO: 실제 파일/결과 확인 후 상태 판단 로직으로 교체
    return [
        {"phase": "Phase 1", "name": "시드 구축",  "detail": "", "status": "wait"},
        {"phase": "Phase 2", "name": "시드 검증",  "detail": "", "status": "wait"},
        {"phase": "Phase 3", "name": "대화 생성",  "detail": "", "status": "wait"},
        {"phase": "Phase 4", "name": "품질 검증",  "detail": "", "status": "wait"},
    ]

def get_data_stats():
    """현재까지 생성된 데이터 통계를 반환. 본인 결과 파일 기준으로 수정."""
    # TODO: 실제 결과 파일에서 통계를 계산하는 로직으로 교체
    # 예시:
    # results = list(RESULT_DIR.glob("*.jsonl"))
    # completed = sum(count_lines(f) for f in results)
    return {
        "completed": 0,
        "pass_rate": 0,
        "avg_turns": 0,
    }

def get_issues():
    """현재 이슈 목록 반환."""
    # TODO: 필요 시 이슈 추가
    return [
        # {"severity": "info", "text": "이슈 내용", "date": "2026-04-23"},
    ]


# ═══════════════════════════════════════════════════════════════
#  아래는 수정하지 마세요 — 자동 집계 + 대시보드 동기화
# ═══════════════════════════════════════════════════════════════

def _build_summary():
    """파이프라인 결과를 summary dict로 자동 조립."""
    stats = get_data_stats()
    return {
        "id": TASK_ID,
        "name": TASK_NAME,
        "desc": TASK_DESC,
        "status": TASK_STATUS,
        "info": {
            "tier": TIER,
            "target": TARGET,
            "minimum": MINIMUM,
            "lang_ratio": LANG_RATIO,
            "cot_ratio": COT_RATIO,
        },
        "seeds": SEEDS,
        "crossDims": CROSS_DIMS,
        "dataStats": stats,
        "pipeline": get_pipeline_status(),
        "issues": get_issues(),
        "_updated": datetime.now().isoformat(),
    }


def _save_and_sync():
    """summary 저장 + 대시보드 동기화."""
    summary = _build_summary()

    # 로컬 저장
    out = RESULT_DIR / "summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), "utf-8")
    print(f"\n[summary] {out} 저장 완료")

    # 대시보드 동기화 (수정 불필요 — 파이프라인 실행 시 자동 전송)
    _WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"
    try:
        import urllib.request
        data = json.dumps(summary, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(_WEBHOOK, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=30)
        print("[dashboard] 동기화 완료")
    except Exception as e:
        print(f"[dashboard] 동기화 실패 (무시): {e}")


def main():
    """파이프라인 실행. 끝나면 자동으로 대시보드에 반영됩니다."""
    print(f"{'='*50}")
    print(f"  {TASK_ID} {TASK_NAME}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    build_seeds()
    validate_seeds()
    generate_dialogues()
    validate_quality()

    # ── 자동 집계 + 대시보드 동기화 (수정 불필요) ──
    _save_and_sync()

    print(f"\n{'='*50}")
    print("  파이프라인 완료")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
