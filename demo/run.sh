#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
VENV="${WORK}/venv"
trap 'rm -rf "${WORK}"' EXIT

python3 -m venv "${VENV}"
"${VENV}/bin/pip" install --quiet --upgrade pip
"${VENV}/bin/pip" install --quiet -e "${ROOT}"

echo "==> Version"
"${VENV}/bin/sicario" --version

echo "==> Passing governed example"
"${VENV}/bin/sicario" verify "${ROOT}/examples/python-api"
echo "exit=$?"

echo "==> Deliberately failing governed example"
set +e
"${VENV}/bin/sicario" verify "${ROOT}/examples/python-api-failing"
rc=$?
set -e
echo "exit=${rc}"

if [[ "${rc}" -eq 0 ]]; then
  echo "expected failing example to halt"
  exit 1
fi
