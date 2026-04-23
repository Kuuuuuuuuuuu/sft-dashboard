# 대시보드 자동 연동 통합

> 이 파일을 Claude Code에 주고 "이거 실행해줘"라고 하면 됩니다.
> 현재 프로젝트의 파이프라인을 자동으로 찾아서 대시보드 sync 코드를 붙입니다.

---

## 지시사항

아래 단계를 순서대로 수행하세요.

### 1단계: 파이프라인 메인 스크립트 찾기

현재 프로젝트에서 메인 파이프라인 스크립트를 찾으세요.

탐색 우선순위:
1. `scripts/` 또는 `script/` 디렉토리의 `generate_*.py`, `run_*.py`, `main.py`, `pipeline.py`
2. 프로젝트 루트의 `main.py`, `run.py`, `pipeline.py`
3. `if __name__` 패턴이 있는 Python 파일 중 가장 큰 것
4. 최근 수정된 `.py` 파일

찾은 파일 경로를 기록합니다.

### 2단계: 파이프라인 결과 구조 분석

메인 스크립트를 읽고 아래 항목들을 추출할 수 있는지 파악하세요.

**필수 추출 항목:**
- `results` 또는 최종 결과 리스트 변수명
- 결과 저장 경로 (jsonl, json 파일)

**추출 가능하면 가져올 항목:**
| 항목 | 찾는 패턴 | summary 필드 |
|------|-----------|-------------|
| 완료 건수 | `len(results)`, 결과 리스트 길이 | `dataStats.completed` |
| 통과율 | `pass_cnt`, `format_ok`, validation 결과 | `dataStats.pass_rate` |
| 평균 턴 수 | `messages` 배열 길이, `turns` 변수 | `dataStats.avg_turns` |
| 언어 분포 | `language` 필드, `ko`/`en` 카운트 | `dataStats.lang` |
| CoT 분포 | `cot_mode`, `think`/`no_think` 카운트 | `dataStats.cot` |
| 도메인 분포 | `domain` 필드 집계 | `dataStats.domains` |
| 횡단차원 | `cross_cutting`, `dimension` 필드 | `crossDims` |
| 파이프라인 단계 | 함수명, Phase 구분, 로그 메시지 | `pipeline` |

**코드에 없는 항목은 기본값(0, 빈 배열)을 넣습니다. 절대 에러를 내지 마세요.**

### 3단계: 태스크 기본정보 확인

프로젝트에서 아래 정보를 찾으세요:
- README.md, CLAUDE.md, 또는 프로젝트 설명 파일에서 태스크 ID, 이름, 설명
- 설정 파일(yaml, json, py 상단)에서 target, minimum, tier 등

못 찾으면 사용자에게 물어보세요:
```
태스크 ID가 뭔가요? (예: G4-1, G4-2, ...)
```

### 4단계: sync 코드 생성 및 삽입

메인 스크립트의 **맨 마지막** (또는 `if __name__ == "__main__"` 블록의 마지막)에 아래 패턴의 코드를 삽입하세요.

**2단계에서 파악한 변수명과 구조에 맞게 코드를 조정하세요.**

```python
# ============================================================
# 대시보드 자동 동기화 (수정 불필요)
# ============================================================
try:
    # ── 여기서 위 코드의 변수들을 활용하여 통계 집계 ──
    # 예시 (실제 변수명에 맞게 수정):
    # _completed = len(results)
    # _pass_rate = round(pass_cnt / len(results) * 100) if results else 0
    # _turns = [len([m for m in r["messages"] if m["role"] in ("user","assistant")]) for r in results]
    # _avg_turns = round(sum(_turns)/len(_turns), 1) if _turns else 0

    _summary = {
        "id": "TASK_ID",           # ← 3단계에서 확인한 값
        "name": "TASK_NAME",       # ← 3단계에서 확인한 값
        "desc": "TASK_DESC",       # ← 3단계에서 확인한 값
        "status": "wip",
        "info": {
            "tier": 0,             # ← 3단계에서 확인한 값
            "target": 0,
            "minimum": 0,
            "lang_ratio": "",
            "cot_ratio": "",
        },
        "seeds": [],               # ← 시드 정보가 있으면 채우기
        "crossDims": [],           # ← 횡단차원 정보가 있으면 채우기
        "dataStats": {
            "completed": 0,        # ← 2단계에서 추출한 값
            "pass_rate": 0,
            "avg_turns": 0,
            "lang": {},
            "cot": {},
            "domains": [],
        },
        "pipeline": [
            {"phase": "Phase 1", "name": "시드 구축",  "detail": "", "status": "wait"},
            {"phase": "Phase 2", "name": "시드 검증",  "detail": "", "status": "wait"},
            {"phase": "Phase 3", "name": "대화 생성",  "detail": "", "status": "wait"},
            {"phase": "Phase 4", "name": "품질 검증",  "detail": "", "status": "wait"},
        ],
        "issues": [],
    }

    # 로컬 저장
    import json as _json
    from pathlib import Path as _Path
    _out = _Path("result/summary.json")
    _out.parent.mkdir(parents=True, exist_ok=True)
    _out.write_text(_json.dumps(_summary, ensure_ascii=False, indent=2), "utf-8")

    # Google Sheets 전송
    import urllib.request as _ur
    _WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"
    _req = _ur.Request(_WEBHOOK, data=_json.dumps(_summary, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"})
    _ur.urlopen(_req, timeout=30)
    print("[dashboard] 동기화 완료")
except Exception as _e:
    print(f"[dashboard] 동기화 실패 (무시): {_e}")
```

### 5단계: 검증

1. 삽입한 코드의 변수명이 실제 파이프라인 코드와 일치하는지 확인
2. `try/except`로 감싸져 있어서 실패해도 파이프라인에 영향 없음을 확인
3. import 충돌이 없는지 확인 (별칭 `_json`, `_Path`, `_ur` 사용)

### 주의사항

- **파이프라인 코드는 절대 수정하지 마세요.** 맨 끝에 추가만 합니다.
- 기존 변수를 읽기만 하고 덮어쓰지 마세요.
- sync 실패가 파이프라인을 중단시키면 안 됩니다.
- 추출할 수 없는 항목은 기본값을 넣으세요. 에러보다 빈 데이터가 낫습니다.
