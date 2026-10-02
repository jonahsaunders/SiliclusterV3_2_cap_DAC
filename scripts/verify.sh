#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PDK=sky130A PDK_ROOT=/foss/pdks PDKPATH=/foss/pdks/sky130A
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1
export SPICE_USERINIT_DIR="$ROOT/scripts/ngspice"
python3 scripts/physical_verify.py
python3 scripts/check_layout.py
python3 scripts/rebuild_verify.py
# Verify native-exported KiCad connectivity and recorded source hashes.
python3 scripts/check_schematic.py
python3 scripts/extract.py
if [[ "${1:-}" == "--smoke" ]]; then
    python3 scripts/qualify.py probe --name ci_probe --netlist "$ROOT/netlist/silicluster_jonah_2cap_dac.rc.spice"
    python3 scripts/smoke_check.py
    exit 0
fi
python3 scripts/prepare_models.py
for suite in ac pvt mc full; do
    python3 scripts/qualify_suite.py "$suite" --jobs "${JOBS:-4}"
done
python3 scripts/special.py
python3 scripts/buffer_noise.py
python3 scripts/release_report.py
python3 scripts/render_docs.py
python3 scripts/write_docs.py
