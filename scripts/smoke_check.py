"""Require an actual extracted-layout transfer in the CI smoke run."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1]
r=json.loads((P/'verification/signoff/ci_probe_result.json').read_text())
assert r['monotonic'] and r['selected_endpoint_inl_lsb']<1
assert r['max_ripple_uv']<100
assert r['gds_sha256']==hashlib.sha256((P/'gds/silicluster_jonah_2cap_dac.gds').read_bytes()).hexdigest()
assert r['netlist_sha256']==hashlib.sha256((P/'netlist/silicluster_jonah_2cap_dac.rc.spice').read_bytes()).hexdigest()
print('Extracted-layout CI probe passes monotonicity, selected INL, ripple, and evidence hashes.')
