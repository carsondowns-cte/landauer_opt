#!/usr/bin/env bash
# Comprehensive lint + test sweep (macOS/Linux)
set -euo pipefail
LOG=check_log.txt
ENV=.venv_test

echo "=== 0. new virtual-env  ==="
python3 -m venv "$ENV"
source "$ENV/bin/activate"
python -m pip install -q --upgrade pip

echo "=== 1. install package ===" | tee $LOG
pip install -e .[dev] >> $LOG 2>&1

# detect correct package path (flat vs src layout)
PKG_PATH=""
for p in landauer_opt src/landauer_opt; do
  [[ -d $p ]] && PKG_PATH=$p && break
done
[[ -z $PKG_PATH ]] && { echo "package dir not found" | tee -a $LOG; exit 1; }
echo "using package path: $PKG_PATH" | tee -a $LOG

echo "=== 2. Ruff lint ===" | tee -a $LOG
ruff check "$PKG_PATH" tests | tee -a $LOG

echo "=== 3. Black style ===" | tee -a $LOG
black --check "$PKG_PATH" tests | tee -a $LOG

echo "=== 4. Pytest unit ===" | tee -a $LOG
pytest -q | tee -a $LOG

echo "All checks passed; full log saved to $LOG"