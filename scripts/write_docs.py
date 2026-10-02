"""Write the README and submission draft from audited final-layout results."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]
s=json.loads((P/'verification/summary.json').read_text())
person=json.loads((P/'participant.json').read_text())
assert s['gds_sha256']==hashlib.sha256((P/'gds/silicluster_jonah_2cap_dac.gds').read_bytes()).hexdigest()
readme=f'''# Silicluster v3 - two-capacitor serial DAC

An 8-bit serial charge-sharing DAC in SKY130, prepared as a **180 × 115 µm analog macro** for Silicluster v3. This version repacks the [original circuit](https://github.com/jonahsaunders/tt_sky130_um_2_cap_DAC/tree/b67d9ecd2a2fc5518c4d116b158384e28da9a48c) into 20,700 µm², a {s['area_reduction_from_source_pct']:.1f}% area reduction, while preserving device sizes and conversion capacitance. It uses the call's required vertical M4 / horizontal M5 power grid.

**Integration detail still open:** the call does not explicitly allocate digital phase inputs to analog projects or provide a physical pin template. This circuit needs three digital inputs in addition to its two analog reference inputs and one analog output. The current M4 pin positions are provisional. [Organizer questions](docs/organizer_questions.md) and [the submission checklist](docs/submission.md) identify the confirmations needed. The circuit has not been emailed, accepted, fabricated, or measured on silicon.

## Circuit and layout

![Connected editable schematic](docs/images/schematic_overview.png)

The two conversion banks are nominally 6.454 pF each, with sixteen MIM units per bank in a common-centroid array. A separate C3 capacitor compensates the output buffer. Three externally timed phases charge, isolate, and share the capacitor banks; eight bits arrive LSB first. The ideal output is `0.2 V + 0.7 V × code / 256`.

![Actual compact GDS layout](docs/images/layout_overview.png)

The image is rendered from the delivered GDS, including the power grid and capacitor array. Native layout and GDS both compare uniquely to the schematic with no device-property errors. Pin rectangles are checked across GDS, LEF, SPICE, and the Verilog interface. [Architecture and historical reference](docs/architecture.md).

## Results from this layout

| Check | Result |
|---|---|
| Full GDS DRC / antenna | 0 violations / 0 feedback |
| Native and GDS LVS | Unique match; no property errors |
| Schematic ERC / connectivity | 0 violations; 72 visible device connections checked |
| Fresh rebuild | Identical circuit and GDS polygon geometry |
| Complete transfer sweeps | 9 × 256 codes; all strictly monotonic |
| Worst endpoint INL | {s['worst_full_endpoint_inl_lsb']:.4f} LSB |
| DNL range | {s['min_full_dnl_lsb']:.4f} to {s['max_full_dnl_lsb']:.4f} LSB |
| PVT selected-code points / mismatch seeds | 30 / 32 |
| Buffer stability | 120 cases; minimum phase margin {s['min_phase_margin_deg']:.2f}° |
| Full-range standalone buffer step | Worst half-LSB settling {s['max_buffer_settling_0p5lsb_us']:.2f} µs; allow 8 µs |
| Hold drift over 50 µs at 85 °C | At most {s['max_hold_drift_50us_lsb']:.5f} LSB in tested cases |

![Post-layout transfer, INL, DNL, and mismatch](docs/images/linearity.png)

These are **model-based extracted-layout results**. Endpoint INL removes offset and gain. Accurate absolute voltage needs calibration: the 32 mismatch samples have endpoint offsets from {s['mc_offset_range_mv'][0]:.2f} to {s['mc_offset_range_mv'][1]:.2f} mV. The sampled tests do not establish silicon yield or measured ENOB. The fixture uses assumed analog series resistance and capacitance; final Silicluster pads may require retesting. [Full validation document, conditions, and limitations](verification/verification.md) · [printable validation PDF](verification/silicluster_validation.pdf) · [native schematic PDF](schematic/suarez_dac.pdf) · [all full-code measurements](verification/all_code_results.csv) · [machine-readable summary](verification/summary.json).

![Stability and buffer settling](docs/images/stability_settling.png)

## Use and reproduce

Nominal supply is 1.8 V; tested references are 0.2/0.9 V and output loading is 5–20 pF with 10 MΩ DC impedance. Initialize for 8 µs. Each bit uses 2 µs charge, 0.2 µs dead time, 2 µs share, and 0.2 µs dead time. Read 3 µs after bit 7. Including the inter-word gap, conversion takes 46.9 µs (about 21.3 kwords/s). HIGH and LOW must never overlap. [Interface, timing, calibration, and bring-up](docs/operation.md) · [hardware-neutral controller example](examples/phase_driver.py).

The pinned IIC OSIC Tools environment runs `bash scripts/verify.sh --smoke` for physical checks, a fresh build, and an extracted-layout transfer probe. `bash scripts/verify.sh` reruns full qualification and regenerates documentation. Native KiCad export instructions are included separately. [Reproduction guide](docs/reproduce.md).

## Package contents

| Folder/file | Purpose |
|---|---|
| `gds/`, `layout/`, `lef/` | Final mask data, Magic top/child cells, integration abstract |
| `src/project.v` | Analog macro's external interface only |
| `schematic/` | Editable KiCad project, native PDF/SVG, detail images |
| `netlist/` | Reference circuit, LVS, coupled-C, raw and reduced RC |
| `sim/`, `verification/signoff/` | Testbenches, model dependencies, cases, results, logs |
| `verification/verification.md` | Simulation and validation document |
| `scripts/` | Deterministic generators, physical checks, qualification, reporting, packaging |
| `requirements/` | Supplied full Silicluster v3 call |
| `docs/`, `participant.json` | Integration checklist, organizer/submission drafts, participant details |
| `manifest.json` | Hashes of release contents |

The compact release ZIP includes the call's required analog artifacts and a verified manifest. Repeated DUT snapshots and bulk per-run waveform vectors are regenerated by the scripts. The final GDS SHA-256 is `{s['gds_sha256']}`. Tool/source versions and extraction assumptions are in [provenance](provenance.json); PDK model redistribution notices are in [third-party notices](THIRD_PARTY_NOTICES.md).

Participant: {person['name']}, {person['affiliation']}, {person['country']}. City still needs to be filled in before sending the submission email. The supplied call gives a deadline of October 31, 2026, 11:59 p.m. Mexico City time, subject to remaining slots and technical acceptance. See [submission draft](docs/submission_email.md).
'''
(P/'README.md').write_text(readme,encoding='utf-8')
draft=f'''# Final submission email draft

To: {person['submission_email']}

Subject: Silicluster v3 analog submission - two-capacitor serial DAC

Hello Silicluster team,

Please find attached the ZIP package for my Silicluster v3 analog project, a SKY130 8-bit two-capacitor serial charge-sharing DAC with a buffered output.

Participant: {person['name']}
Affiliation: {person['affiliation']}
City: {person['city'] or '[FILL CITY BEFORE SENDING]'}
Country: {person['country']}
Project name: {person['project_name']}
Project type: {person['project_type']}

The macro occupies exactly 180 × 115 µm and uses nominal 1.8 V power with vertical M4 and horizontal M5 power rails. It has two analog reference inputs, one buffered analog output, and three 1.8 V digital phase-control inputs. The package includes final GDS, Magic cells, the external-interface Verilog file, simulation testbenches and models, the validation document, and successful DRC/LVS evidence.

Extracted-layout qualification includes nine complete 256-code sweeps, 30 PVT probes, 32 local-mismatch seeds, and 120 stability cases. All complete sweeps are monotonic; worst endpoint INL is {s['worst_full_endpoint_inl_lsb']:.4f} LSB and minimum tested phase margin is {s['min_phase_margin_deg']:.2f} degrees. Accurate absolute output requires offset/gain calibration.

Repository: https://github.com/jonahsaunders/SiliclusterV3_2_cap_DAC

Thank you,
{person['name']}

---

Before sending: fill the city, obtain organizer confirmation for the analog project's digital phase pins and physical pin/PDN template, incorporate any requested changes and rerun qualification, then attach the current `silicluster_v3_2cap_dac.zip`. This is a prepared draft, not a sent email. Do not represent provisional pins as organizer-approved.
'''
(P/'docs/submission_email.md').write_text(draft,encoding='utf-8')
print('Wrote README and participant submission draft from audited results.')
