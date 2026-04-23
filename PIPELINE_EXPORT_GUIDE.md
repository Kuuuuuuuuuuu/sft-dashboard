# 파이프라인 자동 리포팅 가이드

> 파이프라인 코드에 아래 내용을 적용하면, 실행할 때마다 대시보드에 자동으로 결과가 반영됩니다.

---

## 구조

```
파이프라인 실행
   ↓
result/summary.json 생성 (표준 스키마)
   ↓
dashboard_sync.py 가 Google Sheets에 POST
   ↓
대시보드 자동 반영
```

---

## 1. 환경변수 설정 (1회)

관리자에게 받은 webhook URL을 환경변수로 등록합니다.

### Windows (영구 설정)
```cmd
setx DASHBOARD_WEBHOOK_URL "https://script.google.com/macros/s/여기에_URL/exec"
```

### Linux / Mac
```bash
echo 'export DASHBOARD_WEBHOOK_URL="https://script.google.com/macros/s/여기에_URL/exec"' >> ~/.bashrc
source ~/.bashrc
```

---

## 2. dashboard_sync.py 복사

`scripts/dashboard_sync.py` 파일을 본인 프로젝트에 복사합니다.
외부 라이브러리 설치 필요 없음 (Python 기본 라이브러리만 사용).

---

## 3. 파이프라인에 연동

### 방법 A: 코드에서 직접 호출

```python
from dashboard_sync import sync

# 파이프라인 결과를 summary dict로 정리
summary = {
    "id": "G4-1",
    "name": "도메인 전문가 롤플레이",
    "desc": "30개 도메인 전문가 페르소나 기반 전문 상담 대화",
    "status": "wip",

    "info": {
        "tier": 2,
        "target": 3500,
        "minimum": 1000,
        "lang_ratio": "EN:KO = 5:5",
        "cot_ratio": "think 30% / no_think 70%"
    },

    "dataStats": {
        "completed": len(results),      # ← 파이프라인에서 계산
        "pass_rate": pass_rate,          # ← 파이프라인에서 계산
        "avg_turns": avg_turns,          # ← 파이프라인에서 계산
    },

    "pipeline": [
        {"phase": "Phase 1", "name": "시드 구축",  "detail": "...", "status": "done"},
        {"phase": "Phase 2", "name": "시드 검증",  "detail": "...", "status": "done"},
        {"phase": "Phase 3", "name": "대화 생성",  "detail": "...", "status": "wip"},
        {"phase": "Phase 4", "name": "품질 검증",  "detail": "...", "status": "wait"},
    ],

    "issues": [
        {"severity": "info", "text": f"현재 {len(results)}건 완료", "date": "2026-04-23"}
    ],

    # seeds, crossDims 등은 변경 없으면 생략 가능
}

# 대시보드에 전송 (실패해도 파이프라인은 멈추지 않음)
sync("G4-1", summary)
```

### 방법 B: JSON 파일로 저장 후 CLI 실행

```python
import json
from pathlib import Path

# 파이프라인 끝에서 summary 저장
Path("result/summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), "utf-8"
)
```

```bash
# 파이프라인 실행 후
python dashboard_sync.py G4-1 result/summary.json
```

---

## 4. summary 필수 필드

전체 스키마는 `task_summary_template.md` 참고. 최소한 아래 필드만 보내도 됩니다:

```json
{
  "id": "G4-1",
  "status": "wip",
  "dataStats": {
    "completed": 100,
    "pass_rate": 85,
    "avg_turns": 12
  },
  "pipeline": [
    {"phase": "Phase 1", "name": "시드 구축", "detail": "", "status": "done"},
    {"phase": "Phase 2", "name": "시드 검증", "detail": "", "status": "done"},
    {"phase": "Phase 3", "name": "대화 생성", "detail": "", "status": "wip"},
    {"phase": "Phase 4", "name": "품질 검증", "detail": "", "status": "wait"}
  ]
}
```

나머지 필드(name, desc, info, seeds 등)는 기존 값이 유지됩니다.

---

## 5. 파이프라인 단계 이름 (통일)

모든 태스크 공통:

| phase | name |
|-------|------|
| Phase 1 | 시드 구축 |
| Phase 2 | 시드 검증 |
| Phase 3 | 대화 생성 |
| Phase 4 | 품질 검증 |

detail만 태스크별로 다르게 작성하세요.

---

## 6. 동기화 실패 시

- 파이프라인은 정상 진행됩니다 (동기화 실패가 파이프라인을 멈추지 않음)
- `[dashboard_sync] 동기화 실패` 로그가 나오면 관리자에게 알려주세요
- 수동 방법: `result/summary.json`을 관리자에게 전달하면 직접 반영
