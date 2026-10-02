# Reproduce the design and checks

The design environment is [IIC OSIC Tools](https://github.com/iic-jku/IIC-OSIC-TOOLS), release 2026.07, pinned to:

```
hpretl/iic-osic-tools@sha256:5d6adf1f437cd0f2f8f8614488ec3c247ba8c768f4663a25d5e997b30ccb13b0
```

It supplies Magic 8.3.678, netgen 1.5.323, ngspice 46, KLayout, and SKY130A. Run commands from the repository root. The `bash -lc` shell initializes this image's tool paths. On Linux/macOS, a smoke check can be launched with:

```sh
docker run --rm --user 0:0 --entrypoint bash \
  -v "$PWD:/foss/designs" \
  hpretl/iic-osic-tools@sha256:5d6adf1f437cd0f2f8f8614488ec3c247ba8c768f4663a25d5e997b30ccb13b0 \
  -lc 'cd /foss/designs && bash scripts/verify.sh --smoke'
```

The explicit container user permits writes to bind mounts whose owner differs from the image's default user. On Linux, generated files may be owned by root; use a suitable user mapping for your local setup if desired. For the full flow, omit `--smoke`. Use `JOBS=4` to bound concurrent qualification processes. Full tests can take tens of minutes and generate substantial raw waveform data under `verification/signoff/`; these regenerable vectors and DUT snapshots are ignored by Git and omitted from compact packages.

The smoke check performs full GDS DRC, native/GDS LVS, antenna checks, geometry/interface auditing, a fresh layout/circuit rebuild, a check of the native-exported schematic snapshot, and ten extracted-layout conversion codes. It is not a rerun of all 2,304 full-sweep measurements. The full flow extracts new coupled capacitance and RC, prepares models, runs AC/PVT/mismatch/full-code suites, startup/settling/hold/numerical/noise tests, audits hashes and acceptance criteria, and regenerates figures, README, and validation text.

To intentionally regenerate the source circuit or layout:

```sh
python3 scripts/build_circuit.py
python3 scripts/build_layout.py
python3 scripts/physical_verify.py
python3 scripts/extract.py
```

Run full qualification after any physical/electrical change. The release audit refuses result files carrying a different GDS or RC hash. GDS timestamps can change on rebuild; polygon equivalence is tested independently. Native cell masters referenced by the top-level .mag are all supplied in `layout/`. For Magic, open that directory with the SKY130A technology file. When importing GDS use `gds maskhints yes` to preserve the narrow resistor's 1.27 µm URPM implant hint.

## Schematic workflow

KiCad 10.0.6 native CLI exported the included schematic artifacts. Regenerate the connected drawing with `python3 scripts/build_schematic.py`, then run native KiCad ERC and exports. On Windows:

```powershell
./scripts/export_schematic.ps1
```

On Linux with compatible native KiCad CLI:

```sh
kicad-cli sch erc --exit-code-violations -o verification/schematic_erc.rpt schematic/suarez_dac.kicad_sch
kicad-cli sch export netlist --format kicadxml -o verification/schematic_netlist.xml schematic/suarez_dac.kicad_sch
kicad-cli sch export svg --exclude-drawing-sheet --draw-hop-over -o schematic/render schematic/suarez_dac.kicad_sch
kicad-cli sch export pdf --draw-hop-over -o schematic/suarez_dac.pdf schematic/suarez_dac.kicad_sch
python3 scripts/check_schematic.py
```

The IIC OSIC image does not supply KiCad. CI checks the supplied native-exported snapshot and its recorded source hash; it does not claim to run native ERC again. Run the native export after schematic edits. The source is editable without external symbol installation: custom symbols are embedded and the supplied library table points to the project-local library.

## Testbench portability and packaging

All saved `.spice` decks in the compact package use paths relative to the repository root. Execute them there, for example `SPICE_USERINIT_DIR="$PWD/scripts/ngspice" ngspice -b verification/signoff/full_tt_block000.spice`. The generators calculate absolute paths from their own location when regenerating/running a suite, avoiding dependence on an author's machine paths. Cached SKY130 models are supplied; the optional full-PDK model-equivalence case uses the PDK installed in the pinned image.

The project supplies an explicit simulator initialization, with native BSIM4 interpretation, one simulation thread, and behavioral-resistor thermal noise enabled. Simulation generators and `verify.sh` select it through `SPICE_USERINIT_DIR`, avoiding the multi-PDK image's inherited IHP OSDI preloads. Nominal and mismatch ten-code checks of this initialization agree with the original qualification setup within 0.021 µV, well inside the existing 10 µV numerical-equivalence criterion; `verification/simulator_init.json` records the comparison. Noise results are rerun with behavioral-resistor noise enabled.

`python3 scripts/package_release.py` audits existing results, compacts testbench paths, writes `manifest.json`, and creates a verified ZIP under `outputs/` when run in this workspace, or under the chosen `--output` directory elsewhere. A later full run regenerates redundant DUT snapshots and full vectors. The package retains AC loop-injection netlists and special waveforms required by the plots.

Macro checks are not organizer integration checks. No fixed Silicluster analog pin template was found. See [the checklist](submission.md) before describing the design as fully approved for integration.
