# SFT 대시보드 연동 가이드

## 이 문서는 무엇인가요?

SFT 데이터 구축 프로젝트의 진행 현황을 대시보드에 자동으로 올려주는 가이드입니다.

각 태스크 담당자가 이 문서의 내용을 **Claude Code에 붙여넣고 "실행해줘"**라고 하면, Claude가 프로젝트 폴더를 분석해서 대시보드용 JSON 파일을 만들고 Jupyter 서버에 업로드합니다.

**대시보드 URL:** http://172.19.181.250:8888/view/sft_dashboard.html

---

## 전체 흐름

```
1. 이 문서를 Claude Code에 붙여넣기
2. Claude가 프로젝트 폴더 분석 → JSON 파일 생성
3. JSON 파일을 Jupyter 서버에 업로드
4. 대시보드에서 확인
```

---

## Claude Code가 지켜야 할 규칙

1. **사용자에게 질문하지 마세요.** 필요한 정보는 프로젝트 파일에서 직접 찾으세요.
2. **데이터를 임의로 만들지 마세요.** 파일에서 못 찾은 항목은 빈 값(`0`, `""`, `[]`)을 넣으세요.
3. **system prompt를 임의로 만들지 마세요.** 프로젝트에서 못 찾으면 없이 보내세요.
4. **파이프라인 단계명은 고정입니다.** 시드 구축 → 시드 검증 → 대화 생성 → 품질 검증. 변경하지 마세요.

---

## 1단계: 프로젝트 탐색

프로젝트 폴더 전체를 탐색해서 아래 정보를 수집하세요.

### 어디서 찾나요?

| 찾을 정보 | 주로 있는 위치 |
|-----------|---------------|
| 태스크 ID·이름·설명·Tier | `README.md`, `CLAUDE.md`, 폴더명 |
| 목표/최소 수량, 언어/CoT 비율 | `README.md`, `*.yaml`, `config/`, 코드 상단 상수 |
| 시드 데이터 종류·수량 | `data/`, `seed/`, `prompt/` 폴더 |
| 파이프라인 진행 상태 | 코드의 Phase 구분, 로그 파일, 결과 파일 유무 |
| 생성 프롬프트 | `prompt/`, `prompts/` 폴더의 `.txt` 파일 |

---

## 2단계: 결과 파일 파싱

생성된 대화 데이터 파일(`.jsonl` 또는 `.json`)을 찾아서 통계를 집계하세요.

### 결과 파일은 어디 있나요?

프로젝트마다 다릅니다. 아래 순서대로 찾으세요:
1. `result/`, `result/live/`, `results/`
2. `output/`, `outputs/`
3. `summary/`, `data/output/`
4. 프로젝트 루트의 `.jsonl` 파일
5. 가장 최근 수정된 `.jsonl` 파일

### 무엇을 집계하나요?

| 항목 | 집계 방법 |
|------|-----------|
| 완료 건수 | 결과 파일의 총 레코드 수 |
| 통과율 | `format_ok`, `passed` 등 검증 필드에서 pass 비율 |
| 평균 턴 수 | 각 레코드의 `messages`에서 user+assistant 수의 평균 |
| 언어 분포 | `language` 필드별 건수 (`{"KO": 20, "EN": 19}`) |
| CoT 분포 | `cot_mode` 필드별 건수 (`{"think": 12, "no_think": 27}`) |
| 카테고리 분포 | `domain`, `category`, `type` 등 분류 필드별 건수 |
| 횡단차원 비율 | `cross_cutting` 필드에서 각 차원의 비율(%) 계산 |
| 횡단차원 턴 분포 | 각 횡단차원에 해당하는 레코드의 턴 수를 집계 (`{"10": 12, "14": 4}`) |

---

## 3단계: 구축 예시 추출

결과 파일에서 **횡단차원별 1건씩** 대표 샘플을 추출하세요.

- 멀티턴 변형 1건
- 장문맥 1건
- 부정적 지시 1건
- 출력 형식 제어 1건

각 샘플에는 `messages` 배열 전체(system + user + assistant 턴제 대화)를 포함하세요.

---

## 4단계: JSON 파일 생성

아래 스키마에 맞는 `summary_G4-{n}.json` 파일을 만드세요.

```json
{
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

  "seeds": [
    {
      "name": "전문가 페르소나 풀",
      "count": 30,
      "category": "D (Synthetic)",
      "usage": "자체 생성 — 의사, 변호사, 엔지니어 등",
      "contamination": "오염 위험 없음"
    }
  ],

  "crossDims": [
    {"name": "멀티턴 변형",    "target": 40, "actual": 56, "turnDist": {"10": 12, "12": 3, "14": 4}},
    {"name": "장문맥",         "target": 20, "actual": 22, "turnDist": {"5": 1, "6": 2, "10": 3}},
    {"name": "부정적 지시",    "target": 25, "actual": 19, "turnDist": {"4": 3, "8": 2, "10": 1}},
    {"name": "출력 형식 제어", "target": 15, "actual": 3,  "turnDist": {"10": 1}}
  ],

  "dataStats": {
    "completed": 39,
    "pass_rate": 85,
    "avg_turns": 9.2,
    "lang": {"KO": 20, "EN": 19},
    "cot": {"think": 12, "no_think": 27},
    "domains": [
      {"name": "내과학", "count": 5},
      {"name": "법학", "count": 4}
    ]
  },

  "pipeline": [
    {"phase": "Phase 1", "name": "시드 구축", "detail": "페르소나 30명, 레퍼런스 260건 생성", "status": "done"},
    {"phase": "Phase 2", "name": "시드 검증", "detail": "GPT 전수 검증, 탈락→대체→재평가", "status": "done"},
    {"phase": "Phase 3", "name": "대화 생성", "detail": "Gemma4 31B-it, 39/3500건 완료", "status": "wip"},
    {"phase": "Phase 4", "name": "품질 검증", "detail": "포맷/사실/품질 3단계 검증", "status": "wait"}
  ],

  "issues": [
    {"severity": "info", "text": "39건 완료 / 3500 목표", "date": "2026-04-24"},
    {"severity": "warn", "text": "15턴 이상 대화에서 truncation 발생", "date": "2026-04-23"}
  ],

  "prompts": {
    "system": "대화 생성 시 사용한 시스템 프롬프트 전체 내용",
    "user": "유저 프롬프트 템플릿",
    "eval": "품질 검증 시 사용한 평가 프롬프트"
  },

  "samples": [
    {
      "id": "G4-01-00001",
      "language": "en",
      "cot_mode": "no_think",
      "cross_cutting": ["long_context"],
      "messages": [
        {"role": "system", "content": "You are Rehabilitation Physician..."},
        {"role": "user", "content": "Hello, Doctor..."},
        {"role": "assistant", "content": "I can hear how concerning this is..."},
        {"role": "user", "content": "That sounds hopeful..."},
        {"role": "assistant", "content": "That is a very insightful question..."}
      ],
      "metadata": {
        "persona_name_ko": "재활의학과 전문의",
        "persona_name_en": "Rehabilitation Physician",
        "domain": "재활의학",
        "auto_validation": {"format_ok": true},
        "quality_validation": {"score": 4, "passed": true, "issues": ["검증 코멘트"]}
      }
    }
  ]
}
```

---

## 필드 설명

### 기본 정보

| 필드 | 필수 | 값 | 설명 |
|------|------|----|------|
| `id` | O | `"G4-1"` ~ `"G4-6"` | 본인 태스크 번호 |
| `name` | O | 문자열 | 태스크 이름 |
| `desc` | O | 문자열 | 한 줄 설명 |
| `status` | O | `"done"` / `"wip"` / `"wait"` | 현재 진행 상태 |

### info (태스크 사양)

| 필드 | 필수 | 값 | 설명 |
|------|------|----|------|
| `tier` | O | 1~3 | 태스크 난이도 |
| `target` | O | 숫자 | 목표 수량 |
| `minimum` | O | 숫자 | 최소 수량 |
| `lang_ratio` | O | `"EN:KO = 5:5"` | 언어 비율 |
| `cot_ratio` | O | `"think 30% / no_think 70%"` | CoT 비율 |

### seeds (시드 데이터)

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | O | 데이터셋 이름 |
| `count` | O | 시드 데이터 수량 |
| `category` | - | 분류 (기본: `"D (Synthetic)"`) |
| `usage` | O | 어떻게 사용하는지 |
| `contamination` | - | 비고 (기본: `"-"`) |

### crossDims (횡단차원 매트릭스)

4개 고정. 이름을 변경하지 마세요.

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | O | `"멀티턴 변형"` / `"장문맥"` / `"부정적 지시"` / `"출력 형식 제어"` |
| `target` | O | 목표 비율 (%) |
| `actual` | O | 현재 실제 비율 (%). 데이터 없으면 `0` |
| `turnDist` | O | 해당 차원의 턴 수별 건수. 예: `{"10": 12, "14": 4}`. 데이터 없으면 `{}` |

### dataStats (데이터 통계)

| 필드 | 필수 | 설명 |
|------|------|------|
| `completed` | O | 현재까지 완료된 샘플 수. 데이터 없으면 `0` |
| `pass_rate` | O | 검증 통과율 (%). 데이터 없으면 `0` |
| `avg_turns` | O | 평균 대화 턴 수. 데이터 없으면 `0` |
| `lang` | O | 언어별 건수. 예: `{"KO": 20, "EN": 19}`. 데이터 없으면 `{}` |
| `cot` | O | CoT별 건수. 예: `{"think": 12, "no_think": 27}`. 데이터 없으면 `{}` |
| `domains` | - | 카테고리별 건수 배열. 예: `[{"name":"내과학","count":5}]` |

### pipeline (구축 프로세스)

4단계 고정. **이름(name)은 변경하지 마세요.** `detail`과 `status`만 수정하세요.

| 필드 | 필수 | 설명 |
|------|------|------|
| `phase` | O | `"Phase 1"` ~ `"Phase 4"` |
| `name` | O | `"시드 구축"` / `"시드 검증"` / `"대화 생성"` / `"품질 검증"` (고정) |
| `detail` | O | 이 태스크에서 해당 단계가 구체적으로 무엇을 하는지 |
| `status` | O | `"done"` / `"wip"` / `"wait"` |

### issues (이슈)

선택 항목입니다. 없으면 빈 배열 `[]`.

| 필드 | 설명 |
|------|------|
| `severity` | `"error"` / `"warn"` / `"info"` |
| `text` | 이슈 내용 |
| `date` | `"YYYY-MM-DD"` |

### prompts (생성 프롬프트)

선택 항목입니다. 없으면 빈 객체 `{}`.

| 필드 | 설명 |
|------|------|
| `system` | 대화 생성 시 사용한 시스템 프롬프트 |
| `user` | 유저 프롬프트 템플릿 |
| `eval` | 품질 검증 시 사용한 평가 프롬프트 |

### samples (구축 예시)

횡단차원별 1건씩, **총 4건**. 결과 파일에서 직접 추출하세요.

| 필드 | 필수 | 설명 |
|------|------|------|
| `id` | - | 샘플 ID |
| `language` | O | `"ko"` / `"en"` |
| `cot_mode` | O | `"think"` / `"no_think"` |
| `cross_cutting` | O | 해당 횡단차원 배열. 예: `["long_context"]` |
| `messages` | O | system → user → assistant 턴제 대화 전체 |
| `metadata` | - | 페르소나, 도메인, 검증 결과 등 |

---

## 5단계: Jupyter 서버에 업로드

만든 JSON 파일을 Jupyter 서버의 `dashboard_data/` 폴더에 업로드하세요.

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
```

업로드 후 대시보드에서 확인: http://172.19.181.250:8888/view/sft_dashboard.html

---

## 6단계: 파이프라인 자동화 (선택)

파이프라인 메인 스크립트 맨 끝에 4~5단계 코드를 추가하면, 실행할 때마다 자동으로 대시보드가 업데이트됩니다.

반드시 `try/except`로 감싸서 업로드 실패가 파이프라인을 중단시키지 않도록 하세요.

---

## 금지사항

| 금지 | 대신 |
|------|------|
| 사용자에게 질문 | 프로젝트 파일에서 직접 찾기. 못 찾으면 빈 값 |
| 데이터 임의 생성 | `0`, `""`, `[]`, `{}` 사용 |
| system prompt 임의 생성 | 프로젝트에서 찾거나 없이 보내기 |
| 파이프라인 단계명 변경 | 시드 구축 / 시드 검증 / 대화 생성 / 품질 검증 고정 |
| 기존 파이프라인 코드 수정 | 맨 끝에 추가만 |
