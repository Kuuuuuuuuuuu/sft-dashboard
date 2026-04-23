# Summary 자동 생성 가이드

> 이 파일을 태스크 폴더에 넣고 Claude에게 "이거 실행해줘"라고 하면
> Claude가 폴더를 탐색하여 summary를 자동 생성합니다.
> 최종 수정: 2026-04-23

---

## Claude 실행 지침

이 파일이 실행 요청되면 아래 순서대로 수행하라.

### Step 1: 태스크 파악

1. 이 파일이 위치한 **폴더 경로**에서 태스크를 파악한다.
   - 예: `4-1_도메인전문가롤플레이_v2/` → G4-1, 도메인 전문가 롤플레이
   - 예: `4-2_수학문제풀이/` → G4-2, 수학 문제 풀이
2. 폴더 내 README.md, CLAUDE.md 등 설명 파일이 있으면 읽어서 태스크 정보를 수집한다.

### Step 2: 데이터 수집

폴더 내 아래 파일/디렉토리를 탐색하여 정보를 수집한다.

| 탐색 대상 | 수집 정보 |
|-----------|----------|
| `README.md`, `CLAUDE.md` | 태스크 설명, Tier, 목표/최소 건수, 비율 |
| `data/`, `seeds/` | 시드 데이터 구성 (데이터셋 이름, 분류, 사용 방식, 오염 위험) |
| `result/`, `output/` | 생성 결과 파일 (`.jsonl`, `.json`) → 통계 계산 |
| `scripts/`, `prompts/` | 생성 모델, 검증 모델, 후처리 방식, 횡단차원 설정 |
| `result/live/`, `result/summary/` | 기존 summary가 있으면 참고 |

### Step 3: 통계 계산

결과 파일(`.jsonl`, `.json`)을 읽어 아래 통계를 자동 계산한다.

- 완료 건수, 통과율
- 언어 분포 (KO/EN 건수)
- CoT 분포 (think/no_think 건수)
- 도메인별 건수
- 횡단차원별 목표/실제 비율
- 횡단차원별 턴 수 분포
- 평균 턴 수

### Step 4: 샘플 추출

결과 파일에서 **횡단차원별 최소 1개**의 샘플 대화를 추출한다.

- 샘플은 system 메시지를 **제외**하고 user/assistant 턴만 포함
- think 모드는 `<think>...</think>` 블록 유지
- 라벨: "횡단차원 / 도메인 / CoT모드 / 언어" 형태

### Step 5: summary 저장

수집한 정보를 아래 포맷으로 조립하여 `result/summary/` 폴더에 저장한다.
파일명: `summary_YYYY-MM-DD_HHMMSS.json`

---

## 출력 포맷

```json
{
  "id": "G4-N",
  "name": "태스크명",
  "desc": "태스크 설명",
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
      "name": "데이터셋명",
      "category": "D (Synthetic)",
      "usage": "사용 방식",
      "contamination": "오염 위험 없음"
    }
  ],

  "crossDims": [
    {
      "name": "멀티턴 변형",
      "target": 40,
      "actual": 80,
      "turnDist": { "10": 4, "12": 2 }
    }
  ],

  "dataStats": {
    "completed": 5,
    "pass_rate": 100,
    "avg_turns": 10.0,
    "lang": { "KO": 2, "EN": 3 },
    "cot": { "think": 2, "no_think": 3 },
    "domains": [
      { "name": "재활의학", "count": 1 }
    ]
  },

  "pipeline": [
    { "phase": "Phase 1", "name": "시드 구축", "detail": "세부 내용", "status": "done" },
    { "phase": "Phase 2", "name": "시드 검증", "detail": "세부 내용", "status": "done" },
    { "phase": "Phase 3", "name": "대화 생성", "detail": "세부 내용", "status": "wip" },
    { "phase": "Phase 4", "name": "품질 검증", "detail": "세부 내용", "status": "wait" }
  ],

  "issues": [],

  "samples": [
    {
      "label": "횡단차원 / 도메인 / CoT모드 / 언어",
      "tags": [
        { "text": "횡단차원", "style": "yellow" },
        { "text": "도메인", "style": "yellow" },
        { "text": "no_think", "style": "coral" },
        { "text": "KO", "style": "accent" }
      ],
      "messages": [
        { "role": "user", "content": "..." },
        { "role": "assistant", "content": "..." }
      ]
    }
  ]
}
```

---

## 필수 항목 체크리스트

summary 저장 전 아래 항목이 모두 포함되었는지 확인한다.

| # | 항목 | 확인 |
|---|------|------|
| 1 | 태스크 기본 정보 (id, name, status, info) | |
| 2 | 시드 데이터 (seeds[]) | |
| 3 | 횡단차원 매트릭스 — 목표/실제 비율 (crossDims[]) | |
| 4 | 횡단차원별 턴 수 분포 (crossDims[].turnDist) | |
| 5 | 언어 분포 (dataStats.lang) | |
| 6 | CoT 분포 (dataStats.cot) | |
| 7 | 도메인/카테고리 분포 (dataStats.domains) | |
| 8 | 구축 프로세스 4단계 상세 (pipeline[]) | |
| 9 | 횡단차원별 샘플 대화 최소 1개 (samples[]) | |
| 10 | 이슈 로그 — 해당 시 (issues[]) | |

---

## 시드 데이터 분류 기준

| 코드 | 의미 |
|------|------|
| `A (Human-authored)` | 사람이 직접 작성 |
| `B (Licensed)` | 라이선스 데이터 |
| `C (Public Dataset)` | 공개 데이터셋 |
| `D (Synthetic)` | 자체 생성/합성 |

---

## 샘플 태그 스타일

| style | 색상 | 용도 |
|-------|------|------|
| `accent` | 파랑 | 언어 (EN, KO) |
| `teal` | 청록 | think 모드 |
| `coral` | 코랄 | no_think 모드 |
| `yellow` | 노랑 | 도메인, 횡단차원 |

---

## 횡단차원별 샘플 요구사항

각 횡단차원의 특성이 샘플 대화에 드러나야 한다.

| 횡단차원 | 샘플에서 확인되어야 하는 특징 |
|----------|------------------------------|
| 멀티턴 변형 | 10턴 이상의 긴 대화, 주제가 심화/전환됨 |
| 장문맥 | 긴 맥락 유지, 페르소나 배경이 상세히 반영됨 |
| 부정적 지시 | 사용자가 제약 조건을 걸고, 어시스턴트가 모든 턴에서 준수 |
| 출력 형식 제어 | 사용자가 특정 형식(이메일, 표, 목록 등)을 요청하고 해당 형식으로 응답 |

---

## 파이프라인 상태값

| status | 의미 |
|--------|------|
| `done` | 완료 |
| `wip` | 진행중 |
| `wait` | 대기 |

---

## 정보가 부족할 때

파일 탐색으로 수집할 수 없는 정보가 있으면:
1. 해당 필드를 빈 값 또는 0으로 채운다.
2. 사용자에게 부족한 항목을 알려주고 보충을 요청한다.
3. 보충 후 다시 summary를 생성한다.
