# Final submission email draft

To: silicluster@gmail.com

Subject: Silicluster v3 analog submission - two-capacitor serial DAC

Hello Silicluster team,

Please find attached the ZIP package for my Silicluster v3 analog project, a SKY130 8-bit two-capacitor serial charge-sharing DAC with a buffered output.

Participant: Jonah Saunders
Affiliation: Independent designer
City: [FILL CITY BEFORE SENDING]
Country: United States
Project name: Silicluster v3 two-capacitor serial DAC
Project type: Analog

The macro occupies exactly 180 × 115 µm and uses nominal 1.8 V power with vertical M4 and horizontal M5 power rails. It has two analog reference inputs, one buffered analog output, and three 1.8 V digital phase-control inputs. The package includes final GDS, Magic cells, the external-interface Verilog file, simulation testbenches and models, the validation document, and successful DRC/LVS evidence.

Extracted-layout qualification includes nine complete 256-code sweeps, 30 PVT probes, 32 local-mismatch seeds, and 120 stability cases. All complete sweeps are monotonic; worst endpoint INL is 0.5526 LSB and minimum tested phase margin is 71.25 degrees. Accurate absolute output requires offset/gain calibration.

Repository: https://github.com/jonahsaunders/SiliclusterV3_2_cap_DAC

Thank you,
Jonah Saunders

---

Before sending: fill the city, obtain organizer confirmation for the analog project's digital phase pins and physical pin/PDN template, incorporate any requested changes and rerun qualification, then attach the current `silicluster_v3_2cap_dac.zip`. This is a prepared draft, not a sent email. Do not represent provisional pins as organizer-approved.
