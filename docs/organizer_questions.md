# Organizer clarification draft

To: silicluster@gmail.com

Subject: Silicluster v3 analog DAC: digital control pins and physical interface

Hello Silicluster team,

I am preparing an analog SKY130 two-capacitor serial DAC for Silicluster v3. It fits exactly within 180 × 115 µm, uses a nominal 1.8 V supply, and implements vertical M4 and horizontal M5 power rails. It has two analog reference inputs, one buffered analog output, and three 1.8 V digital phase-control inputs (`charge_high`, `charge_low`, and `share`). The compact macro passes local DRC/LVS and extracted-layout simulation.

Could you confirm whether an analog project may use these three digital input pins in addition to its analog I/O? Does the digital-project I/O allocation, clock/reset access, or remote-control capability also apply to analog projects?

Please share the analog macro pin/interface template and required physical power-rail landing coordinates, widths, and naming conventions. Are the provisional edge M4 signal pins acceptable, or should I use fixed pin locations? I would also appreciate the intended analog pad/input/output parasitics and the final DRC/LVS integration flow so I can check against the same assumptions.

Project repository: https://github.com/jonahsaunders/SiliclusterV3_2_cap_DAC

Thank you,
Jonah Saunders

---

This is a draft for the participant to send. No message has been sent. The required final submission email is separate and must include the participant's affiliation and city/country plus the current release ZIP.
