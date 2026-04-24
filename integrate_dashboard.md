# 대시보드 연동 가이드

> Claude Code에 이 파일 내용을 붙여넣고 "실행해줘"라고 하면 됩니다.
> 아래 스키마에 맞는 JSON 파일을 만들어서 Jupyter 서버에 업로드합니다.

---

## 규칙

1. **사용자에게 질문하지 마세요.** 프로젝트 파일에서 직접 찾으세요.
2. **데이터를 임의로 만들지 마세요.** 못 찾으면 빈 값을 넣으세요.
3. **system prompt를 임의로 만들지 마세요.** 못 찾으면 없이 보내세요.

---

## 출력 파일

`summary_G4-{n}.json` 1개를 만들어서 Jupyter 서버에 업로드합니다.

**업로드 방법:**
```python
import requests, json

s = requests.Session()
r = s.get("http://172.19.181.250:8888/login")
xsrf = s.cookies.get("_xsrf", "")
s.post("http://172.19.181.250:8888/login",
    data={"_xsrf": xsrf, "password": "mtdt2023"},
    headers={"X-XSRFToken": xsrf})

content = open("summary_G4-1.json", "r", encoding="utf-8").read()
s.put("http://172.19.181.250:8888/api/contents/dashboard_data/summary_G4-1.json",
    json={"type": "file", "format": "text", "name": "summary_G4-1.json", "content": content},
    headers={"X-XSRFToken": xsrf})
```

---

## 스키마

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
    {"name": "장문맥", "target": 20, "actual": 22, "turnDist": {"5": 1, "10": 3}},
    {"name": "부정적 지시", "target": 25, "actual": 19, "turnDist": {"4": 3, "8": 2}},
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
  ],

  "prompts": {
    "system": "시스템 프롬프트 전체 내용",
    "user": "유저 프롬프트 템플릿",
    "eval": "평가 프롬프트"
  },

  "samples": [
    {
      ... 결과 파일의 레코드를 그대로 가져오세요 (아래 설명 참고) ...
    }
  ]
}
```

---

## 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `id` | O | G4-1 ~ G4-6 |
| `name` | O | 태스크 이름 |
| `desc` | O | 한 줄 설명 |
| `status` | O | `done` / `wip` / `wait` |
| `info.*` | O | tier, target, minimum, lang_ratio, cot_ratio |
| `seeds[]` | O | name, count, category, usage, contamination |
| `crossDims[]` | O | 4개 고정: 멀티턴 변형 / 장문맥 / 부정적 지시 / 출력 형식 제어 |
| `crossDims[].turnDist` | O | 턴 수별 건수 `{"10": 12, "14": 4}` |
| `dataStats` | O | completed, pass_rate, avg_turns, lang, cot, domains |
| `pipeline[]` | O | 4개 고정 (이름 변경 금지), detail과 status만 수정 |
| `issues[]` | - | severity(`error`/`warn`/`info`), text, date |
| `prompts` | - | system, user, eval 프롬프트 텍스트 |
| `samples[]` | O | 횡단차원별 1건씩, 총 4건. 결과 파일의 레코드를 **그대로** 가져오세요 (아래 상세 참고) |

---

## 실행 순서

### 1단계: 프로젝트 탐색

`README.md`, `CLAUDE.md`, `*.yaml`, `config/`, `data/`, `result/`, `scripts/`를 읽고 위 스키마의 모든 필드를 채우세요.

### 2단계: 결과 파일 파싱

프로젝트에서 결과 파일을 찾으세요. 폴더명은 프로젝트마다 다릅니다.

탐색 우선순위:
1. `result/`, `result/live/`, `results/`
2. `output/`, `outputs/`
3. `summary/`, `data/output/`
4. 프로젝트 루트의 `.jsonl`, `.json` 파일
5. 가장 최근 수정된 `.jsonl` 파일

찾은 파일을 Python으로 읽어서 `dataStats`, `crossDims.actual`, `crossDims.turnDist`를 집계하세요.

### 3단계: 구축 예시 추출

결과 파일에서 횡단차원별 1건씩 추출하여 `samples` 배열을 만드세요.

**중요: 결과 파일의 레코드를 있는 그대로 가져오세요.**

- 각 태스크마다 레코드 구조(필드명, metadata 형태)가 다릅니다. 그대로 두세요.
- metadata에 어떤 필드가 있든 전부 포함하세요. 필드를 삭제하거나 이름을 바꾸지 마세요.
- messages 배열도 원본 그대로 가져오세요. system 메시지가 있으면 포함, 없으면 없는 대로.
- 대시보드가 자동으로 레코드의 필드를 분석해서 태그와 메타데이터 카드를 만듭니다.

```python
# 횡단차원별 1건씩 선택하는 예시
picked = {}
for r in results:
    # cross_cutting 필드명은 태스크마다 다를 수 있음
    cc_field = r.get("cross_cutting") or r.get("cross_cutting_dimension") or []
    if isinstance(cc_field, str): cc_field = [cc_field]
    for cc in cc_field:
        dim = cc if isinstance(cc, str) else str(cc)
        if dim not in picked:
            picked[dim] = r  # 레코드 전체를 그대로

samples = list(picked.values())  # 이걸 그대로 samples에 넣으세요
```

### 4단계: JSON 저장

위 스키마에 맞는 `summary_G4-{n}.json` 파일을 프로젝트 루트에 저장하세요.

### 5단계: Jupyter 업로드

4단계에서 만든 JSON을 Jupyter 서버에 업로드하세요.

```python
import requests
s = requests.Session()
r = s.get("http://172.19.181.250:8888/login")
xsrf = s.cookies.get("_xsrf", "")
s.post("http://172.19.181.250:8888/login",
    data={"_xsrf": xsrf, "password": "mtdt2023"},
    headers={"X-XSRFToken": xsrf})

content = open("summary_G4-1.json", "r", encoding="utf-8").read()
r = s.put("http://172.19.181.250:8888/api/contents/dashboard_data/summary_G4-1.json",
    json={"type": "file", "format": "text", "name": "summary_G4-1.json", "content": content},
    headers={"X-XSRFToken": xsrf})
print(f"업로드: {r.status_code}")
print("대시보드: http://172.19.181.250:8888/view/sft_dashboard.html")
```

### 6단계: 파이프라인에 자동화 (선택)

파이프라인 맨 끝에 4~5단계 코드를 `try/except`로 감싸서 추가하면, 실행할 때마다 자동 업로드됩니다.

---

## 금지

- 사용자에게 질문
- 데이터 임의 생성
- system prompt 임의 생성
- 파이프라인 단계명 변경 (시드 구축 / 시드 검증 / 대화 생성 / 품질 검증 고정)
