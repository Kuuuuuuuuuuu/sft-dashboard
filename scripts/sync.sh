#!/bin/bash
# ═══════════════════════════════════════════════════════
#  SFT Dashboard — Summary 자동 동기화
#  본인 태스크 번호와 소스 경로만 수정하세요
# ═══════════════════════════════════════════════════════
TASK_ID="G4-1"
SUMMARY_SOURCE=""    # 비우면 기존 JSON 유지, 경로 넣으면 복사

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR" || exit 1

echo "[sync] $(date '+%Y-%m-%d %H:%M:%S') — $TASK_ID"

# 1. pull
git pull --rebase origin main 2>/dev/null || git pull origin main

# 2. summary 복사
TARGET="data/summary_${TASK_ID}.json"
if [ -n "$SUMMARY_SOURCE" ] && [ -f "$SUMMARY_SOURCE" ]; then
  cp "$SUMMARY_SOURCE" "$TARGET"
  echo "[sync] copied → $TARGET"
fi

# 3. 변경 확인
if git diff --quiet -- "$TARGET" && git diff --cached --quiet -- "$TARGET"; then
  echo "[sync] no changes"
  exit 0
fi

# 4. commit + push
git add "$TARGET"
git commit -m "update $TASK_ID summary ($(date '+%Y-%m-%d %H:%M'))"
git push origin main || {
  echo "[sync] retry..."
  git pull --rebase origin main
  git push origin main
}

echo "[sync] done"
