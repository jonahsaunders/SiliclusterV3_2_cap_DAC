# Source and third-party notices

The circuit and generators are adapted from Jonah Saunders's [two-capacitor DAC repository](https://github.com/jonahsaunders/tt_sky130_um_2_cap_DAC), source commit `b67d9ecd2a2fc5518c4d116b158384e28da9a48c`. This separate repository targets Silicluster v3. Author ownership is retained; this file does not grant a new license for the project.

`sim/models/sky130_*.spice` contains a derived cache of the used model families from the SkyWater SKY130 PDK. Copyright 2020 The SkyWater PDK Authors. These files are licensed under Apache License 2.0; the complete license is included in `sim/models/LICENSE.txt`. The cache generator preserves parameter expressions and geometry bins for the six used families. Model reduction to used families is documented in the file header and `scripts/prepare_models.py`.

Magic device geometry is generated using the open SKY130 PDK included in the pinned IIC OSIC Tools image. The full toolchain and underlying PDK remain governed by their respective licenses; they are not redistributed inside this repository. `provenance.json` records the tool image, versions, and design source.

The supplied Silicluster participation PDF is included as the project's requirements reference. Rights in that document belong to its author. Inclusion does not imply organizer approval of this design.

The historical charge-sharing conversion principle is credited in [the architecture document](docs/architecture.md). No original-paper figures are copied into this repository; schematic, layout, and results figures are generated from this project's files.
