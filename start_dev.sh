#!/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "${BACKEND_PID}" 2>/dev/null || true
  fi
  if [[ -n "${UI_PID:-}" ]]; then
    kill "${UI_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

python "${ROOT_DIR}/backend/manage.py" runserver 0.0.0.0:8000 &
BACKEND_PID=$!

npm --prefix "${ROOT_DIR}/ui" run dev &
UI_PID=$!

wait "${BACKEND_PID}" "${UI_PID}"
