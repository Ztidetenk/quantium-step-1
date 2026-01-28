bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

VENV_DIR="venv"
if [ -d ".venv" ]; then
  VENV_DIR=".venv"
fi

if [ -f "$VENV_DIR/bin/activate" ]; then
  # macOS/Linux venv
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
  # Windows venv (Git Bash)
  # shellcheck disable=SC1090
  source "$VENV_DIR/Scripts/activate"
else
  echo "ERROR: Could not find a virtual environment to activate."
  echo "Looked for: .venv or venv"
  exit 1
fi

python -m pytest -q
