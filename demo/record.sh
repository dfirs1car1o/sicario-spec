#!/usr/bin/env bash
# Regenerate the SicarioSpec verify demo recording (cast + GIF).
#
# Produces:
#   demo/verify-demo.cast  — asciinema v2 recording of a REAL terminal session
#   demo/verify-demo.gif   — GIF rendered from the cast via `agg`
#
# Requirements (install once):
#   pip install asciinema
#   brew install agg            # or: cargo install --git https://github.com/asciinema/agg
#
# The recording installs the package into a throwaway venv and runs the real
# CLI. No output is fabricated; re-running this script reproduces the asset.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DIR="${REPO_ROOT}/demo"
CAST="${DEMO_DIR}/verify-demo.cast"
GIF="${DEMO_DIR}/verify-demo.gif"

WORK="$(mktemp -d)"
VENV="$(mktemp -d)/venv"
trap 'rm -rf "${WORK}" "$(dirname "${VENV}")"' EXIT

echo "==> Creating throwaway venv and installing sicario-spec (editable)"
python3 -m venv "${VENV}"
"${VENV}/bin/pip" install --quiet --upgrade pip
"${VENV}/bin/pip" install --quiet -e "${REPO_ROOT}"

echo "==> Staging a clean scratch workspace with the repo examples"
cp -R "${REPO_ROOT}/examples" "${WORK}/examples"

# Make the venv's `sicario` and the scenario driver available to the recording.
export PATH="${VENV}/bin:${PATH}"
cp "${DEMO_DIR}/scenario.sh" "${WORK}/scenario.sh"
chmod +x "${WORK}/scenario.sh"

echo "==> Recording the session with asciinema"
( cd "${WORK}" && asciinema rec \
    --overwrite \
    --cols 100 --rows 32 \
    --command "bash ./scenario.sh" \
    "${CAST}" )

echo "==> Rendering GIF with agg"
agg --theme monokai --font-size 20 "${CAST}" "${GIF}"

echo "==> Done:"
echo "    ${CAST}"
echo "    ${GIF}"
