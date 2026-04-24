# 대시보드 자동 연동 통합

> 이 파일을 Claude Code에 주고 "이거 실행해줘"라고 하면 됩니다.
> 사용자에게 질문하지 말고 프로젝트를 직접 탐색하여 모든 정보를 수집하세요.

---

## 핵심 원칙

**사용자에게 질문하지 마세요.** 모든 정보는 프로젝트 파일에 있습니다.
- 태스크 ID? → README.md, CLAUDE.md, 설정 파일에서 찾으세요.
- 파이프라인 구조? → 코드를 읽으세요.
- 결과 통계? → 결과 파일을 직접 파싱하세요.
- 못 찾은 항목? → 기본값(0, 빈 배열)을 넣으세요. 질문하지 마세요.

---

## 실행 순서

### 1단계: 프로젝트 전체 탐색 (질문 금지 — 직접 찾기)

Explore 에이전트를 사용해서 프로젝트를 **매우 철저하게** 탐색하세요.

```
탐색 대상 (모두 읽으세요):
├── README.md, CLAUDE.md, docs/*.md     → 태스크 ID, 이름, 목적, Tier, 목표/최소 수량
├── *.yaml, *.json, config/             → 언어 비율, CoT 비율, 설정값
├── data/, seed/, prompt/               → 시드 데이터 종류, 수량, 프롬프트 파일
├── result/, output/, log/              → 결과 파일 (.jsonl, .json), 로그
├── scripts/, script/, src/             → 파이프라인 코드
└── 프로젝트 루트의 모든 .py 파일       → 메인 스크립트 후보
```

**추출해야 할 정보 (파일에서 직접 읽기):**

| 정보 | 찾는 위치 | 못 찾으면 |
|------|-----------|-----------|
| 태스크 ID (G4-1~6) | README, CLAUDE.md, 폴더명, 코드 주석 | 폴더명에서 추론 |
| 태스크 이름/설명 | README, CLAUDE.md | 폴더명 사용 |
| Tier | README, 설정 파일 | `0` |
| 목표/최소 수량 | README, 설정 파일, 코드 상단 상수 | `0` |
| 언어 비율 | README, 설정 파일, 코드 상수 | `""` |
| CoT 비율 | README, 설정 파일, 코드 상수 | `""` |
| 시드 데이터 | data/, seed/ 폴더 내 파일들 | `[]` |
| 파이프라인 단계 | 코드의 Phase 구분, 함수명, 로그 메시지 | 기본 4단계 |
| 완료 건수 | result/*.jsonl 라인 수 | `0` |
| 통과율 | 결과 파일의 validation 필드 집계 | `0` |
| 평균 턴 수 | 결과 파일의 messages 배열 길이 평균 | `0` |
| 언어/CoT 분포 | 결과 파일의 language/cot_mode 필드 집계 | `{}` |
| 도메인/카테고리 분포 | 결과 파일의 domain/category/type 필드 집계 | `[]` |
| 횡단차원 | 결과 파일의 cross_cutting/dimension 필드 집계 | `[]` |
| 이슈 | 로그 파일의 에러 패턴, 낮은 통과율 등 | `[]` |

### 2단계: 결과 파일 직접 파싱

결과 파일(.jsonl, .json)을 Python으로 직접 읽어서 통계를 집계하세요.

```python
# 이런 식으로 Bash 도구에서 직접 실행
python -c "
import json
from pathlib import Path

# 결과 파일 찾기 (여러 경로 시도)
for p in ['result', 'result/live', 'output', '.']:
    files = list(Path(p).glob('*.jsonl')) if Path(p).exists() else []
    if files: break

results = []
for f in files:
    for line in f.read_text('utf-8').splitlines():
        if line.strip():
            try: results.append(json.loads(line))
            except: pass

print(f'총 {len(results)}건')
# ... 여기서 통계 집계
"
```

**반드시 집계해야 할 것:**
- `len(results)` → completed
- 통과율: `format_ok`, `passed`, `valid` 등의 필드 찾아서 집계
- 턴 수: `messages` 배열에서 user+assistant 수
- 언어: `language`, `lang` 필드
- CoT: `cot_mode`, `cot` 필드
- 카테고리: `domain`, `category`, `type`, `class` 등 의미 있는 분류 필드
- 횡단차원: `cross_cutting`, `cross_cutting_dimension`, `dimension` 필드
- 턴 분포: 횡단차원별로 턴 수 집계 → `turnDist`

### 3단계: 구축 예시(samples) 추출

결과 파일에서 **횡단차원별 1건씩** 대표 샘플을 추출하세요.

```python
# 횡단차원별 1건씩 선택
picked = {}
for r in results:
    for cc in r.get('cross_cutting', r.get('cross_cutting_dimension', [])):
        dim = cc if isinstance(cc, str) else cc.get('name', str(cc))
        if dim not in picked:
            picked[dim] = r
```

**samples 필수 규칙:**
- messages에 `role: "system"` 메시지를 **반드시 첫 번째로 포함**
- 결과 파일에 system이 없으면, 생성 시 사용한 시스템 프롬프트를 프로젝트에서 찾아서 삽입
- 시스템 프롬프트를 못 찾으면 system 없이 넣되, **절대 임의로 만들지 마세요**
- tags: 횡단차원, 도메인, cot_mode, 언어를 태그로

### 4단계: sync 코드를 파이프라인 끝에 삽입

메인 스크립트의 **맨 마지막**에 아래 패턴의 코드를 삽입하세요.
1~3단계에서 파악한 **실제 변수명**과 **실제 데이터 구조**에 맞게 조정하세요.

```python
# ============================================================
# 대시보드 자동 동기화 (수정 불필요)
# ============================================================
try:
    # ── 여기에 실제 변수를 사용한 통계 집계 코드 ──
    # 위 파이프라인 코드에서 사용한 변수명 그대로 활용
    # 예: results, pass_cnt, ko_cnt 등

    _summary = {
        "id": "...",          # 1단계에서 찾은 값
        "name": "...",
        "desc": "...",
        "status": "wip",
        "info": { ... },      # 1단계에서 찾은 값
        "seeds": [ ... ],     # 1단계에서 찾은 값
        "crossDims": [ ... ], # 2단계에서 집계한 값
        "dataStats": { ... }, # 2단계에서 집계한 값
        "pipeline": [ ... ],  # 1단계에서 파악한 단계
        "issues": [ ... ],    # 2단계에서 발견한 이슈
        "samples": [ ... ],   # 3단계에서 추출한 값
    }

    import json as _json
    from pathlib import Path as _Path
    _out = _Path("result/summary.json")
    _out.parent.mkdir(parents=True, exist_ok=True)
    _out.write_text(_json.dumps(_summary, ensure_ascii=False, indent=2), "utf-8")

    import urllib.request as _ur
    _WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"
    _req = _ur.Request(_WEBHOOK, data=_json.dumps(_summary, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"})
    _ur.urlopen(_req, timeout=30)
    print("[dashboard] 동기화 완료")
except Exception as _e:
    print(f"[dashboard] 동기화 실패 (무시): {_e}")
```

### 5단계: 테스트 전송

4단계에서 삽입한 코드를 파이프라인 실행 없이 **바로 테스트**하세요.

1. 2~3단계에서 이미 결과 파일을 파싱했으니, 그 데이터로 `_summary`를 구성
2. Bash 도구로 Python 코드를 실행하여 webhook 전송
3. 전송 결과 출력

```python
import json, urllib.request
_WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"
_data = json.dumps(_summary, ensure_ascii=False).encode("utf-8")
_req = urllib.request.Request(_WEBHOOK, data=_data, headers={"Content-Type": "application/json"})
_resp = urllib.request.urlopen(_req, timeout=60)
print(f"[dashboard] 전송 완료: {_resp.read().decode()}")
print("[dashboard] 확인: https://kuuuuuuuuuuu.github.io/sft-dashboard/")
```

**반드시 5단계까지 완료하세요.** 코드 삽입만 하고 끝내지 마세요.

### 6단계: summary JSON 파일도 저장

`_summary`에 samples를 포함한 전체 데이터를 `result/summary.json`에 저장하세요.
이 파일은 GitHub에 push되어 대시보드의 구축 예시 탭에서 사용됩니다.

---

## 금지사항

1. **사용자에게 질문하지 마세요.** 태스크 ID, 경로, 설정값 등 모든 정보를 직접 찾으세요.
2. **데이터를 임의로 만들지 마세요.** 프로젝트 파일에 없는 정보는 기본값(0, 빈 배열)을 넣으세요.
3. **파이프라인 기존 코드를 수정하지 마세요.** 맨 끝에 추가만 합니다.
4. **sync 실패가 파이프라인을 중단시키면 안 됩니다.** 반드시 `try/except`로 감싸세요.
5. **system prompt를 임의로 생성하지 마세요.** 프로젝트에서 찾거나, 못 찾으면 없이 보내세요.
