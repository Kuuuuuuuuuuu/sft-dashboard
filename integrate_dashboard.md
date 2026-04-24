# 대시보드 연동 가이드

> Claude Code에 이 파일 내용을 붙여넣고 "실행해줘"라고 하면 됩니다.

---

## 규칙

1. **사용자에게 질문하지 마세요.** 프로젝트 파일에서 직접 찾으세요.
2. **데이터를 임의로 만들지 마세요.** 못 찾으면 빈 값을 넣으세요.
3. **파이프라인 기존 코드를 수정하지 마세요.** 맨 끝에 추가만 합니다.

---

## 스키마

아래 JSON을 채워서 webhook으로 POST하세요. 이것이 대시보드에 표시되는 전부입니다.

```json
{
  "id": "G4-1",
  "name": "태스크 이름",
  "desc": "한 줄 설명",
  "status": "wip",

  "info": {
    "tier": 2,
    "target": 3500,
    "minimum": 1000,
    "lang_ratio": "EN:KO = 5:5",
    "cot_ratio": "think 30% / no_think 70%"
  },

  "seeds": [
    {
      "name": "시드 이름",
      "count": 260,
      "category": "D (Synthetic)",
      "usage": "사용 방식",
      "contamination": "비고"
    }
  ],

  "crossDims": [
    {
      "name": "멀티턴 변형",
      "target": 40,
      "actual": 56,
      "turnDist": {"10": 12, "12": 3, "14": 4, "16": 1}
    },
    {"name": "장문맥", "target": 20, "actual": 22, "turnDist": {"5": 1, "6": 2, "8": 1, "10": 3}},
    {"name": "부정적 지시", "target": 25, "actual": 19, "turnDist": {"4": 3, "8": 2, "10": 1}},
    {"name": "출력 형식 제어", "target": 15, "actual": 3, "turnDist": {"10": 1}}
  ],

  "dataStats": {
    "completed": 39,
    "pass_rate": 85,
    "avg_turns": 9.2,
    "lang": {"KO": 20, "EN": 19},
    "cot": {"think": 12, "no_think": 27},
    "domains": [
      {"name": "카테고리명", "count": 5}
    ]
  },

  "pipeline": [
    {"phase": "Phase 1", "name": "시드 구축", "detail": "세부 내용", "status": "done"},
    {"phase": "Phase 2", "name": "시드 검증", "detail": "세부 내용", "status": "done"},
    {"phase": "Phase 3", "name": "대화 생성", "detail": "세부 내용", "status": "wip"},
    {"phase": "Phase 4", "name": "품질 검증", "detail": "세부 내용", "status": "wait"}
  ],

  "issues": [
    {"severity": "info", "text": "이슈 내용", "date": "2026-04-24"}
  ]
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `id` | O | G4-1 ~ G4-6 |
| `name` | O | 태스크 이름 |
| `desc` | O | 한 줄 설명 |
| `status` | O | `done` / `wip` / `wait` |
| `info.tier` | O | 1~3 |
| `info.target` | O | 목표 수량 |
| `info.minimum` | O | 최소 수량 |
| `info.lang_ratio` | O | 언어 비율 텍스트 |
| `info.cot_ratio` | O | CoT 비율 텍스트 |
| `seeds[].name` | O | 시드 데이터셋 이름 |
| `seeds[].count` | O | 수량 |
| `seeds[].category` | - | 분류 (기본: D (Synthetic)) |
| `seeds[].usage` | O | 사용 방식 |
| `seeds[].contamination` | - | 비고 (기본: -) |
| `crossDims[].name` | O | 멀티턴 변형 / 장문맥 / 부정적 지시 / 출력 형식 제어 |
| `crossDims[].target` | O | 목표 비율 (%) |
| `crossDims[].actual` | O | 실제 비율 (%) |
| `crossDims[].turnDist` | O | 턴 수별 건수 `{"10": 12, "14": 4}` |
| `dataStats.completed` | O | 완료 건수 |
| `dataStats.pass_rate` | O | 통과율 (%) |
| `dataStats.avg_turns` | O | 평균 턴 수 |
| `dataStats.lang` | O | 언어별 건수 `{"KO": 20, "EN": 19}` |
| `dataStats.cot` | O | CoT별 건수 `{"think": 12, "no_think": 27}` |
| `dataStats.domains` | - | 카테고리별 건수 |
| `pipeline[].phase` | O | Phase 1~4 |
| `pipeline[].name` | O | 시드 구축 / 시드 검증 / 대화 생성 / 품질 검증 |
| `pipeline[].detail` | O | 세부 설명 |
| `pipeline[].status` | O | `done` / `wip` / `wait` |
| `issues[].severity` | - | `error` / `warn` / `info` |
| `issues[].text` | - | 이슈 내용 |
| `issues[].date` | - | YYYY-MM-DD |

### 구축 예시 (samples)

`data/summary_G4-{n}.json` 파일에 저장합니다. 시트가 아닌 JSON 파일입니다.

횡단차원별 1건씩, 총 4건. 파이프라인 결과 파일에서 직접 추출하세요.

```json
{
  "id": "G4-1",
  "samples": [
    {
      "id": "G4-01-00001",
      "language": "en",
      "cot_mode": "no_think",
      "cross_cutting": ["long_context"],
      "messages": [
        {"role": "system", "content": "시스템 프롬프트 전체"},
        {"role": "user", "content": "사용자 발화"},
        {"role": "assistant", "content": "어시스턴트 응답"}
      ],
      "metadata": {
        "persona_name_ko": "재활의학과 전문의",
        "persona_name_en": "Rehabilitation Physician",
        "domain": "재활의학",
        "auto_validation": {"format_ok": true},
        "quality_validation": {"score": 4, "passed": true, "issues": ["코멘트"]}
      }
    }
  ]
}
```

---

## 실행 순서

### 1단계: 프로젝트 탐색

프로젝트의 `README.md`, `CLAUDE.md`, `*.yaml`, `config/`, `data/`, `result/`, `scripts/`를 읽고 위 스키마의 모든 필드를 채우세요.

### 2단계: 결과 파일 파싱

`result/` 폴더의 `.jsonl`, `.json` 파일을 Python으로 읽어서 `dataStats`, `crossDims`, `turnDist`를 집계하세요.

### 3단계: 구축 예시 추출

결과 파일에서 횡단차원별 1건씩 추출하여 `samples` 배열을 만드세요. system 메시지 필수 포함.

### 4단계: 전송

```python
import json, urllib.request
_WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"
_data = json.dumps(_summary, ensure_ascii=False).encode("utf-8")
_req = urllib.request.Request(_WEBHOOK, data=_data, headers={"Content-Type": "application/json"})
print(urllib.request.urlopen(_req, timeout=60).read().decode())
```

### 5단계: 파이프라인 끝에 sync 코드 삽입

메인 스크립트 맨 끝에 위 전송 코드를 `try/except`로 감싸서 추가하세요. 파이프라인 실행할 때마다 자동 전송됩니다.

### 6단계: 테스트 전송

기존 결과 파일로 즉시 전송하여 대시보드에서 확인하세요.

---

## 금지

- 사용자에게 질문
- 데이터 임의 생성
- 기존 코드 수정
- system prompt 임의 생성 (못 찾으면 없이 보내기)
- 파이프라인 단계명 변경 (시드 구축 / 시드 검증 / 대화 생성 / 품질 검증 고정)
