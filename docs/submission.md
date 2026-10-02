# Silicluster v3 preparation checklist

Requirements come from the [user-supplied full call](../requirements/Silicluster_v3_full_call_for_participation.pdf), read on October 2, 2026. The call is a requirements reference. It does not itself authorize emailing or submitting this design.

| Call requirement | Evidence in this repository | Status |
|---|---|---|
| SKY130, nominal 1.8 V (sections 4, 8) | `design.json`, PDK models, provenance | Implemented |
| 180 × 115 µm analog area (section 9) | GDS, LEF, `verification/layout_geometry.json` | Pass, exact boundary |
| Up to 2 analog inputs / 2 analog outputs (section 8) | Two reference inputs, one buffered output | Within stated analog counts |
| Vertical M4 / horizontal M5 power grid (section 11) | GDS and geometry audit | Implemented and DRC checked |
| Final GDS (section 10) | `gds/silicluster_jonah_2cap_dac.gds` | Included |
| Magic .mag (section 10) | `layout/` top cell and all child cells | Included |
| Verilog external interface only (section 10) | `src/project.v` | Included |
| Testbench and simulation dependencies (section 10) | `sim/`, `netlist/`, `verification/signoff/`, `scripts/` | Included, reproducible |
| Simulation and validation document (section 10) | `verification/verification.md`, figures and CSV | Included |
| Successful DRC evidence (section 10) | `verification/gds_drc.log`, `layout_build.log`, `physical_checks.json` | Pass |
| Successful LVS evidence (section 10) | Native `lvs.log` and re-imported `gds_lvs.log` | Unique match, no property errors |
| Single ZIP (section 10) | Release ZIP with hash manifest | Generated after evidence audit |
| Three digital phase inputs for an analog slot | [Organizer questions](organizer_questions.md) | Confirmation required |
| Signal-pin template and PDN landing positions | Provisional M4 pin rectangles in LEF/GDS | Organizer template required |
| Representative, affiliation, city/country (section 16) | Email draft and `participant.json` | Name, independent affiliation, United States filled; city still needed |

The call gives digital-project pin counts separately from analog-project pin counts. It does not explicitly allocate digital inputs to analog macros. Public material checked on October 2 did not supply a v3 analog physical-interface template. We therefore retain the circuit's three independent phase controls and document provisional pin locations rather than silently treating digital-project allowances as analog-project permission. The cell fits without extra-area allocation.

Current pin rectangles (µm, M4):

| Port | x1 | y1 | x2 | y2 |
|---|---:|---:|---:|---:|
| VGND | 1.4 | 0 | 2.6 | 115 |
| VDPWR | 177.4 | 0 | 178.6 | 115 |
| charge_high | 11.7 | 114.2 | 12.3 | 115 |
| charge_low | 26.7 | 114.2 | 27.3 | 115 |
| share | 41.7 | 114.2 | 42.3 | 115 |
| vref_high | 9.7 | 0 | 10.3 | 0.8 |
| vref_low | 24.7 | 0 | 25.3 | 0.8 |
| vout | 164.7 | 0 | 165.3 | 0.8 |

The power rails meet horizontal M5 at y=1.5 µm (ground) and y=113.5 µm (supply). The stated orientation is implemented, but rail pitch, width, landing coordinates, and top-level naming still require organizer acceptance. Adjusting pins or supply landings requires new DRC/LVS/extraction and qualification evidence; the package hashes prevent old results being reused silently.

The call's deadline is October 31, 2026, 11:59 p.m. Mexico City time. Its 512 slots are assigned first come, subject to technical compliance and availability; the document is not confirmation that a slot remains available. Section 16 requests one ZIP by email to `silicluster@gmail.com` with the representative name, affiliation if applicable, city/country, project name, and analog project type. The repository includes an email draft; no email has been sent. Acceptance does not guarantee a packaged chip, and the call offers remote testing for projects that do not receive one.

Before sending the final ZIP: obtain interface/PDN confirmation, incorporate any required changes and rerun checks, fill participant details, verify the manifest, and attach the current ZIP. Organizer integration/fabrication checks and measured silicon performance remain separate from the local macro qualification.
