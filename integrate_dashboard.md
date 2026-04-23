# 대시보드 자동 연동 통합

> 이 파일을 Claude Code에 주고 "이거 실행해줘"라고 하면 됩니다.
> 현재 프로젝트의 파이프라인을 자동으로 찾아서 대시보드 sync 코드를 붙이고, 바로 테스트 전송까지 합니다.

---

## 지시사항

아래 단계를 순서대로 수행하세요.

### 1단계: 프로젝트 전체 탐색

현재 프로젝트를 깊이 분석하세요. **이 태스크가 무엇을 하는 프로젝트인지** 이해해야 합니다.

**탐색 대상:**
- `README.md`, `CLAUDE.md`, `docs/`, `*.md` — 프로젝트 목적, 태스크 정의, 평가 기준
- `config/`, `*.yaml`, `*.json` — 설정 파일, target/tier/비율 등
- `data/`, `seed/`, `prompt/` — 시드 데이터, 프롬프트
- `result/`, `output/`, `log/` — 기존 실행 결과 파일
- `scripts/`, `script/`, `src/` — 파이프라인 코드 전체

**파악해야 할 것:**
- 이 태스크의 ID, 이름, 목적, Tier
- 목표/최소 수량, 언어 비율, CoT 비율
- **이 태스크만의 고유한 특성** (어떤 종류의 데이터를 만드는가?)

### 2단계: 파이프라인 메인 스크립트 찾기

탐색 우선순위:
1. `scripts/` 또는 `script/` 디렉토리의 `generate_*.py`, `run_*.py`, `main.py`, `pipeline.py`
2. 프로젝트 루트의 `main.py`, `run.py`, `pipeline.py`
3. `if __name__` 패턴이 있는 Python 파일 중 가장 큰 것
4. 최근 수정된 `.py` 파일

메인 스크립트를 **전체** 읽으세요.

### 3단계: 태스크 고유 데이터 식별

이 단계가 핵심입니다. 태스크마다 파이프라인이 다르고 데이터가 다르고 목적이 다릅니다.
**이 태스크에서만 의미 있는 지표와 분포를 찾아내세요.**

#### 공통 항목 (모든 태스크에서 추출)

| 항목 | 찾는 패턴 | summary 필드 |
|------|-----------|-------------|
| 완료 건수 | `len(results)`, 결과 리스트 길이 | `dataStats.completed` |
| 통과율 | `pass_cnt`, `format_ok`, validation 결과 | `dataStats.pass_rate` |
| 평균 턴 수 | `messages` 배열 길이 | `dataStats.avg_turns` |
| 언어 분포 | `language` 필드, `ko`/`en` 카운트 | `dataStats.lang` |
| CoT 분포 | `cot_mode`, `think`/`no_think` 카운트 | `dataStats.cot` |

#### 태스크 고유 항목 (프로젝트에서 발견되는 것에 따라 적응)

각 태스크는 고유한 차원, 카테고리, 지표가 있습니다. 아래는 **예시**입니다.
실제 프로젝트 코드와 결과 파일을 보고 해당 태스크에 맞는 항목을 찾으세요.

**`crossDims` — 이 태스크의 횡단차원/분류 축:**
- 도메인 전문가 롤플레이 → 멀티턴, 장문맥, 부정적 지시, 출력 형식 제어
- 동적 메모리 결합 → 단기기억 활용, 장기기억 결합, 프로필 반영도
- 감정 벡터 → 감정 유형별 분포, 감정 전이 패턴, 서사 구조 유형
- 직교 제약 검증 → 제약 유형별 분포, 동시 적용 제약 수, 위반율
- 톤·스타일 스위칭 → 톤 유형별 분포, 존댓말 단계별 분포, 전환 성공률
- 시스템 프롬프트 준수 → 유혹 유형별 분포, 이탈률, 페르소나 유형별 분포

코드에서 `cross_cutting`, `dimension`, `category`, `type`, `class` 같은 필드를 찾아서
이 태스크의 고유 차원으로 매핑하세요.

**`dataStats.domains` — 이 태스크의 주요 카테고리 분포:**
이름은 "domains"이지만 실제로는 **어떤 카테고리 분포든** 넣을 수 있습니다.
- 도메인 전문가 → 내과학, 법학, 인공지능 등 (실제 도메인)
- 감정 벡터 → 기쁨, 슬픔, 분노, 불안 등 (감정 유형)
- 직교 제약 → 금지어, 형식 제약, 역할 제한 등 (제약 유형)
- 톤 스위칭 → 해요체, 합쇼체, 반말, 사투리 등 (톤 유형)
- 페르소나 준수 → 고객지원, 튜터, 코딩 등 (페르소나 유형)

결과 데이터에서 집계 가능한 의미 있는 카테고리를 찾아서 넣으세요.

**`seeds` — 시드 데이터 정보:**
프로젝트의 `data/`, `seed/`, 설정 파일에서 어떤 시드 데이터를 쓰는지 파악하세요.

**`pipeline` — 파이프라인 단계:**
단계명은 통일하되 (`시드 구축`, `시드 검증`, `대화 생성`, `품질 검증`) detail은 태스크 고유 내용으로 채우세요.
코드에서 Phase 구분, 함수 이름, 로그 메시지를 보고 각 단계가 뭘 하는지 파악하세요.

**`issues` — 현재 이슈:**
로그 파일, 결과 파일의 validation 실패 패턴, 에러 로그 등에서 현재 이슈를 추출하세요.
- 반복되는 실패 패턴이 있으면 warn으로
- 통과율이 낮으면 warn으로
- 진행 상태 요약은 info로

**코드에 없는 항목은 기본값(0, 빈 배열)을 넣습니다. 절대 에러를 내지 마세요.**

### 4단계: sync 코드 생성 및 삽입

메인 스크립트의 **맨 마지막** (또는 `if __name__ == "__main__"` 블록의 마지막)에 아래 패턴의 코드를 삽입하세요.

**3단계에서 파악한 태스크 고유 항목에 맞게 코드를 조정하세요. 아래는 뼈대일 뿐입니다.**

```python
# ============================================================
# 대시보드 자동 동기화 (수정 불필요)
# ============================================================
try:
    # ── 통계 집계: 위 코드의 변수들을 활용 ──
    # 이 부분은 3단계에서 파악한 내용에 따라 태스크별로 달라집니다.
    # 결과 리스트, 통과율, 턴 수, 언어/CoT/도메인 분포,
    # 그리고 이 태스크만의 고유 차원과 카테고리를 집계하세요.

    _summary = {
        "id": "TASK_ID",
        "name": "TASK_NAME",
        "desc": "TASK_DESC",
        "status": "wip",
        "info": {
            "tier": 0,
            "target": 0,
            "minimum": 0,
            "lang_ratio": "",
            "cot_ratio": "",
        },
        "seeds": [],
        "crossDims": [],       # ← 이 태스크의 고유 차원들
        "dataStats": {
            "completed": 0,
            "pass_rate": 0,
            "avg_turns": 0,
            "lang": {},
            "cot": {},
            "domains": [],     # ← 이 태스크의 고유 카테고리 분포
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

### 6단계: 테스트 전송 — 대시보드에 올리기

sync 코드를 삽입한 후, **기존 결과 파일에서 데이터를 수집하여 바로 대시보드에 전송하세요.**

1. 프로젝트의 `result/` (또는 결과 저장 경로)에서 기존 결과 파일 (`.jsonl`, `.json`) 찾기
2. 결과 파일이 있으면 읽어서 3단계에서 설계한 로직으로 통계 집계
3. 결과 파일이 없으면 기본값으로 진행 (completed=0 등)
4. 집계한 `_summary`를 webhook으로 전송하는 Python 코드를 **Bash 도구로 즉시 실행**

```python
import json, urllib.request
# _summary 는 4단계에서 설계한 것과 동일하게 구성
_WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"
_data = json.dumps(_summary, ensure_ascii=False).encode("utf-8")
_req = urllib.request.Request(_WEBHOOK, data=_data, headers={"Content-Type": "application/json"})
_resp = urllib.request.urlopen(_req, timeout=30)
print(f"[dashboard] 테스트 전송 완료: {_resp.read().decode()}")
print("[dashboard] 확인: https://kuuuuuuuuuuu.github.io/sft-dashboard/")
```

**반드시 6단계까지 완료하세요.** 코드 삽입만 하고 끝내지 마세요. 전송까지 해야 대시보드에서 확인할 수 있습니다.

### 주의사항

- **파이프라인 기존 코드는 절대 수정하지 마세요.** 맨 끝에 추가만 합니다.
- 기존 변수를 읽기만 하고 덮어쓰지 마세요.
- sync 실패가 파이프라인을 중단시키면 안 됩니다.
- 추출할 수 없는 항목은 기본값을 넣으세요. 에러보다 빈 데이터가 낫습니다.
- **이 태스크에서만 의미 있는 고유 지표를 적극적으로 찾아 넣으세요.** 모든 태스크가 똑같은 데이터를 보여주면 안 됩니다.
