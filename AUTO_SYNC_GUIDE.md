# Summary 자동 동기화 가이드

> 각 태스크 진행자의 PC에서 summary를 자동 생성 + GitHub push하여 대시보드를 갱신합니다.

## 구조

```
진행자 PC (각자)                          GitHub Pages
┌──────────────────┐    git push         ┌──────────────────┐
│ 파이프라인 실행   │ ──────────────────► │ sft-dashboard/   │
│ → summary JSON   │   매일 자동 or 수동  │   data/          │
│ → git commit     │                     │     summary_G4-1 │
│ → git push       │                     │     summary_G4-2 │
└──────────────────┘                     │     ...          │
                                         │   index.html     │
                                         │   (fetch로 로드)  │
                                         └──────────────────┘
```

---

## 1. 초기 설정 (1회)

### 1-1. 레포 클론

```bash
cd C:\Users\{내계정}\Desktop
git clone https://github.com/Kuuuuuuuuuuu/sft-dashboard.git
cd sft-dashboard
```

### 1-2. 내 태스크 번호 확인

| 진행자 | 태스크 ID | 파일 |
|--------|-----------|------|
| (이름) | G4-1 | `data/summary_G4-1.json` |
| (이름) | G4-2 | `data/summary_G4-2.json` |
| (이름) | G4-3 | `data/summary_G4-3.json` |
| (이름) | G4-4 | `data/summary_G4-4.json` |
| (이름) | G4-5 | `data/summary_G4-5.json` |
| (이름) | G4-6 | `data/summary_G4-6.json` |

### 1-3. 동기화 스크립트 복사

`scripts/sync.sh`가 이미 레포에 포함되어 있습니다. 아래 설정만 수정하세요.

```bash
# scripts/sync.sh 열어서 맨 위 2줄 수정
TASK_ID="G4-1"                    # ← 본인 태스크 번호
SUMMARY_SOURCE=""                 # ← 비우면 기존 JSON 유지 (수동 편집)
```

파이프라인에서 자동 생성하는 경우:
```bash
SUMMARY_SOURCE="C:/Users/me/pipeline/result/live/summary.json"
```

---

## 2. 동기화 스크립트

### scripts/sync.sh (Git Bash / Linux / Mac)

```bash
#!/bin/bash
# ═══════════════════════════════════════
#  설정 — 본인 환경에 맞게 수정
# ═══════════════════════════════════════
TASK_ID="G4-1"
SUMMARY_SOURCE=""
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ═══════════════════════════════════════
#  실행
# ═══════════════════════════════════════
cd "$REPO_DIR" || exit 1

# 1. 최신 pull
git pull --rebase origin main 2>/dev/null || git pull origin main

# 2. summary 복사 (소스가 있으면)
TARGET="data/summary_${TASK_ID}.json"
if [ -n "$SUMMARY_SOURCE" ] && [ -f "$SUMMARY_SOURCE" ]; then
  cp "$SUMMARY_SOURCE" "$TARGET"
  echo "[sync] copied $SUMMARY_SOURCE → $TARGET"
fi

# 3. 변경 확인
if git diff --quiet "$TARGET" 2>/dev/null && ! git ls-files --error-unmatch "$TARGET" >/dev/null 2>&1; then
  echo "[sync] no changes in $TARGET"
  exit 0
fi

# 4. commit + push
git add "$TARGET"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
git commit -m "update $TASK_ID summary ($TIMESTAMP)"
git push origin main

# 충돌 시 재시도 (1회)
if [ $? -ne 0 ]; then
  echo "[sync] push failed, retrying after pull..."
  git pull --rebase origin main
  git push origin main
fi

echo "[sync] done - $TASK_ID updated at $TIMESTAMP"
```

### scripts/sync.bat (Windows CMD용)

```batch
@echo off
REM ═══ 설정 ═══
set TASK_ID=G4-1
set SUMMARY_SOURCE=
set REPO_DIR=%~dp0..

cd /d "%REPO_DIR%"

git pull --rebase origin main 2>nul || git pull origin main

set TARGET=data\summary_%TASK_ID%.json
if defined SUMMARY_SOURCE if exist "%SUMMARY_SOURCE%" (
    copy /y "%SUMMARY_SOURCE%" "%TARGET%" >nul
    echo [sync] copied %SUMMARY_SOURCE%
)

git add "%TARGET%"
for /f "tokens=1-2 delims= " %%a in ('echo %date% %time:~0,5%') do set TS=%%a %%b
git commit -m "update %TASK_ID% summary (%TS%)"
git push origin main || (git pull --rebase origin main && git push origin main)

echo [sync] done
```

---

## 3. 자동 스케줄 설정

### Windows (작업 스케줄러)

1. `Win + R` → `taskschd.msc` 입력
2. 오른쪽 패널 → **기본 작업 만들기**
3. 설정:

| 항목 | 값 |
|------|-----|
| 이름 | `SFT Dashboard Sync` |
| 트리거 | 매일, 오전 9:00 (원하는 시간) |
| 동작 | 프로그램 시작 |
| 프로그램 | `C:\Program Files\Git\bin\bash.exe` |
| 인수 | `C:\Users\{내계정}\Desktop\sft-dashboard\scripts\sync.sh` |
| 시작 위치 | `C:\Users\{내계정}\Desktop\sft-dashboard` |

4. **마침** 클릭

### Linux / Mac (cron)

```bash
# crontab -e
# 매일 09:00에 실행
0 9 * * * /path/to/sft-dashboard/scripts/sync.sh >> /tmp/sft-sync.log 2>&1
```

---

## 4. 수동 실행 (원할 때)

```bash
# Git Bash에서
cd ~/Desktop/sft-dashboard
bash scripts/sync.sh
```

또는 `sync.bat` 더블클릭 (Windows).

---

## 5. 관리자가 전체 수동 트리거

모든 진행자의 summary를 한번에 갱신하고 싶을 때:

```bash
# 관리자 PC에서
cd sft-dashboard
git pull origin main
# → 각 진행자에게 "sync 돌려달라" 연락
# → 또는 진행자가 summary JSON을 직접 보내면 data/ 에 넣고 push
```

---

## 6. summary JSON 자동 생성 (선택)

파이프라인에서 summary를 자동으로 뽑고 싶으면, 아래 Python 스크립트를 참고하세요.

### scripts/export_summary.py (예시)

```python
#!/usr/bin/env python3
"""파이프라인 결과에서 summary JSON 자동 생성."""
import json
from pathlib import Path
from datetime import datetime

# ═══ 설정 — 본인 환경에 맞게 수정 ═══
TASK_ID = "G4-1"
RESULT_DIR = Path("C:/Users/me/pipeline/result/live")
OUTPUT = Path(__file__).parent.parent / "data" / f"summary_{TASK_ID}.json"

def main():
    # 기존 summary 로드 (기본값)
    if OUTPUT.exists():
        summary = json.loads(OUTPUT.read_text("utf-8"))
    else:
        summary = {"id": TASK_ID, "status": "wait"}

    # ── 여기서 파이프라인 결과를 읽어 summary 업데이트 ──

    # 예: 완료 건수 집계
    # dialogues = list(RESULT_DIR.glob("*.jsonl"))
    # summary["dataStats"]["completed"] = sum(count_lines(f) for f in dialogues)

    # 예: 통과율 계산
    # summary["dataStats"]["pass_rate"] = round(passed / total * 100)

    # 예: 파이프라인 상태 업데이트
    # if seeds_ready:
    #     summary["pipeline"][0]["status"] = "done"

    # 타임스탬프
    summary["_updated"] = datetime.now().isoformat()

    # 저장
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), "utf-8")
    print(f"[export] {OUTPUT} updated")

if __name__ == "__main__":
    main()
```

### sync.sh에서 자동 생성 연동

```bash
# sync.sh 맨 위에 추가
python3 scripts/export_summary.py  # summary 생성 후 push
```

---

## 7. 트러블슈팅

### push가 거부될 때
```bash
git pull --rebase origin main
git push origin main
```

### 충돌이 발생할 때
각 진행자는 자기 파일(`data/summary_G4-{N}.json`)만 수정하므로 충돌이 발생하지 않습니다.
만약 발생하면:
```bash
git checkout --theirs data/summary_G4-{다른사람번호}.json
git add .
git rebase --continue
git push origin main
```

### JSON 문법 오류 확인
```bash
python3 -c "import json; json.load(open('data/summary_G4-1.json'))"
# 오류 없으면 OK
```

---

## 체크리스트

- [ ] 레포 클론 완료
- [ ] `scripts/sync.sh` (또는 `.bat`)의 `TASK_ID` 수정
- [ ] `git push` 테스트 (수동으로 한 번 실행)
- [ ] 작업 스케줄러 / cron 등록
- [ ] 대시보드에서 내 태스크 데이터 확인: https://kuuuuuuuuuuu.github.io/sft-dashboard/
