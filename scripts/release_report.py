"""Audit final-layout evidence and write the Silicluster simulation validation document."""
from pathlib import Path
import csv,hashlib,json,re
from qualify import P,Q

V=P/'verification';TOP='silicluster_jonah_2cap_dac'
sha=hashlib.sha256((P/f'gds/{TOP}.gds').read_bytes()).hexdigest()
rcsha=hashlib.sha256((P/f'netlist/{TOP}.rc.spice').read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def current(path):
    result=read(path)
    for r in result if isinstance(result,list) else [result]:
        assert r['gds_sha256']==sha,(path,'stale GDS evidence')
    return result
full=[current(Q/(c[0]+'_result.json')) for c in read(Q/'full_configs.json')]
pvt=[current(Q/f'pvt_{i:02d}_result.json') for i in range(30)]
mc=[current(Q/f'mc_{seed}_result.json') for seed in range(1001,1033)]
ac=[current(path) for path in Q.glob('ac_*_result.json')]
assert len(full)==9 and len(ac)==120
for r in full+pvt+mc+ac:assert r['netlist_sha256']==rcsha
for r in full:
    assert r['full_256_codes'] and [row['code'] for row in r['rows']]==list(range(256))
    assert r['monotonic'] and r['min_dnl_lsb']>-1 and r['max_endpoint_inl_lsb']<1,(r['name'],'linearity failure')
assert all(r['monotonic'] for r in pvt+mc)
assert all(r['phase_margin_deg']>=60 for r in ac)
special=current(Q/'special_results.json');noise=current(Q/'noise_results.json')
assert all(r['netlist_sha256']==rcsha for r in special+noise)
assert special[0]['passes_0p5lsb'] and special[-1]['passes']
steps=[r for r in special if r['name'].startswith('step_')]
hold=[r for r in special if r['name'].startswith('hold_')]
settling=max(s['settling_0p5lsb_us'] for r in steps for s in r['steps'])
assert settling<=8 and all(abs(r['hold_drift_50us_lsb'])<.1 for r in hold)
physical=current(V/'physical_checks.json');geometry=current(V/'layout_geometry.json')
assert physical['full_gds_drc_errors']==0 and physical['antenna_feedback_count']==0
assert geometry['macro_um']==[180,115] and geometry['pin_rectangles_verified_in_gds_and_lef']==8
assert re.search(r'\*\* ERC messages: 0\s+Errors 0\s+Warnings 0',(V/'schematic_erc.rpt').read_text())
schematic=read(V/'schematic_connectivity.json')
assert schematic['schematic_sha256']==hashlib.sha256((P/'schematic/suarez_dac.kicad_sch').read_bytes()).hexdigest()
assert schematic['verified_pin_connections']==72 and not schematic['mismatches']
assert not schematic['property_mismatches'] and not schematic['symbol_pin_mismatches']
rebuild=read(V/'rebuild.json');assert rebuild['netlist_identical'] and rebuild['gds_polygon_geometry_identical']
for model in read(V/'model_cache.json')['corners']:
    assert model['sha256']==hashlib.sha256((P/f"sim/models/sky130_{model['corner']}.spice").read_bytes()).hexdigest()
allcases=full+pvt+mc
summary={'status':'Physical macro qualified in simulation; Silicluster analog digital-pin allocation and pin template await organizer confirmation',
    'platform':'Silicluster v3','macro_um':[180,115],'area_um2':20700,'area_reduction_from_source_pct':(1-20700/(161*225.76))*100,
    'gds_sha256':sha,'rc_sha256':rcsha,'native_and_gds_lvs':'unique match without property errors','gds_drc_errors':0,
    'antenna_feedback_count':0,'schematic_erc_errors':0,'schematic_connections_checked':72,'full_code_sweeps':9,
    'full_code_measurements':2304,'pvt_probe_points':30,'mismatch_seeds':32,'stability_cases':120,
    'min_phase_margin_deg':min(r['phase_margin_deg'] for r in ac),
    'worst_full_endpoint_inl_lsb':max(r['max_endpoint_inl_lsb'] for r in full),
    'min_full_dnl_lsb':min(r['min_dnl_lsb'] for r in full),'max_full_dnl_lsb':max(r['max_dnl_lsb'] for r in full),
    'max_pvt_probe_raw_error_lsb':max(r['max_raw_error_lsb'] for r in pvt),
    'mc_offset_range_mv':[min(r['endpoint_offset_mv'] for r in mc),max(r['endpoint_offset_mv'] for r in mc)],
    'mc_gain_error_range_pct':[min(r['endpoint_gain_error_pct'] for r in mc),max(r['endpoint_gain_error_pct'] for r in mc)],
    'max_supply_current_ua':max(r['max_supply_current_ua'] for r in allcases),
    'max_reference_current_ma':max(r['max_reference_current_ma'] for r in allcases),
    'max_buffer_settling_0p5lsb_us':settling,'max_buffer_overshoot_mv':max(s['overshoot_mv'] for r in steps for s in r['steps']),
    'max_opposite_sample_kick_lsb':max(abs(r['opposite_sample_kick_lsb']) for r in hold),
    'max_hold_drift_50us_lsb':max(abs(r['hold_drift_50us_lsb']) for r in hold),
    'buffer_noise_uv_rms_range':[min(r['integrated_buffer_noise_0p1hz_to_nyquist_uv_rms'] for r in noise),max(r['integrated_buffer_noise_0p1hz_to_nyquist_uv_rms'] for r in noise)],
    'limitations':['Organizer confirmation required for three digital controls on an analog slot and final physical pin/power-rail positions',
        'Offset and gain calibration needed for precise absolute voltage','Discrete PVT points and 32 mismatch seeds do not establish fabrication yield',
        'References fixed at 0.2 V and 0.9 V; arbitrary reference ranges and faster protocols not qualified',
        'Modeled buffer noise and kT/C are not silicon ENOB measurements','No chip-level ESD, padframe, package extraction, or organizer integration checks']}
(V/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (V/'all_code_results.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['case','corner','supply_v','temp_c','load_pf','seed','code','output_v','raw_error_lsb'])
    for r in full:
        for row in r['rows']:writer.writerow([r['name'],r['corner'],r['supply_v'],r['temp_c'],r['load_pf'],r['mismatch_seed'],row['code'],row['output_v'],row['raw_error_lsb']])
table='\n'.join(f"| {r['name']} | {r['corner']} | {r['supply_v']} | {r['temp_c']} | {r['load_pf']} | {r['mismatch_seed'] or '—'} | {r['max_endpoint_inl_lsb']:.4f} | {r['min_dnl_lsb']:.4f} to {r['max_dnl_lsb']:.4f} | {r['max_raw_error_lsb']:.3f} |" for r in full)
report=f'''# Silicluster v3 simulation and validation

The 180 × 115 µm SKY130 macro passes native and independently re-imported GDS LVS, full Magic DRC, gate antenna checks, and the simulation criteria below. This is a prepared analog design package. **Organizer confirmation of digital phase controls and physical pin placement is still required before final submission.** No project acceptance, fabrication, or silicon measurement is claimed.

## Circuit operation and test conditions

C1 and C2 are two nominally 6.454 pF charge-sharing banks, each sixteen 14 × 14 µm MIM units in a common-centroid array. C3 is a separate nominally 1.373 pF buffer compensation capacitor; “two-capacitor DAC” refers to the conversion core. Twenty MOS transistors implement phase inversion, transmission gates, bias, and a unity-gain output buffer. Device sizes and capacitor values are preserved from the [source circuit](https://github.com/jonahsaunders/tt_sky130_um_2_cap_DAC/tree/b67d9ecd2a2fc5518c4d116b158384e28da9a48c); layout and interface are rebuilt for Silicluster.

The ideal result is Vout = 0.2 V + (0.7 V × code / 256). Initialization discharges both banks to Vref_low. For each bit, charge C1 to the selected reference, disconnect both references, then share charge with C2. Eight bits arrive LSB first. The buffer isolates the held charge from the output load.

Supply: nominal 1.8 V, tested boundaries 1.62/1.98 V. Temperatures: −40, 27, 85 °C. Process corners: TT, SS, FF, SF, FS. References: 0.2/0.9 V. Load: 5–20 pF, 10 MΩ DC. Each modeled analog terminal has 500 Ω series resistance; references include 5 pF. This fixture is a conservative test assumption, **not a confirmed Silicluster pad model**. Phase highs track supply.

Initialize for 8 µs with HIGH=0, LOW=1, SHARE=1, then leave all phases off for 0.2 µs. Each bit uses 2 µs charge, 0.2 µs dead time, 2 µs share, 0.2 µs dead time. Read 3 µs after the last share phase: 46.4 µs after word start. An additional 0.5 µs gap gives 46.9 µs/word, about 21.3 kwords/s. The simulated active reset is 7.9 µs within the initialization slot. HIGH and LOW must never overlap; LOW and SHARE overlap only during initialization. No sequencer is hidden in the Verilog black box.

![Timing illustration](../docs/images/timing.png)

## Conversion accuracy

Nine complete 256-code sweeps provide 2,304 code measurements. Five use nominal supply/temperature at each process corner. Two stress conditions are selected from the new layout's PVT probes for highest observed selected-code INL/DNL; two mismatch seeds are selected for highest observed selected-code INL/raw error. Selection is recorded in `signoff/full_configs.json`. These are worst cases **within the sampled probes**, not an exhaustive worst-case claim. Each code is initialized identically; eight ascending codes are grouped per simulation.

All nine complete sweeps are strictly monotonic. Worst endpoint INL is {summary['worst_full_endpoint_inl_lsb']:.4f} LSB; DNL spans {summary['min_full_dnl_lsb']:.4f} to {summary['max_full_dnl_lsb']:.4f} LSB. Acceptance criteria are |endpoint INL| < 1 LSB and every code step positive. Endpoint INL removes offset and gain; raw error retains both. One ideal LSB is 2.734375 mV.

| Case | Corner | VDD (V) | °C | Load (pF) | Seed | Max endpoint INL (LSB) | DNL range (LSB) | Max raw error (LSB) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
{table}

![Transfer and linearity](../docs/images/linearity.png)

Thirty PVT points each test ten selected codes including both endpoints and codes 127/128/129. All selected-code curves are monotonic; maximum raw error is {summary['max_pvt_probe_raw_error_lsb']:.3f} LSB. Thirty-two PDK local-mismatch seeds, with process mismatch disabled, also pass selected-code monotonicity. Their endpoint offset spans {summary['mc_offset_range_mv'][0]:.2f} to {summary['mc_offset_range_mv'][1]:.2f} mV. Accurate absolute voltage needs two-point calibration. See the controller example; calibration cannot extend the measured endpoint range or remove nonlinear error. Sampled mismatch does not establish manufacturing yield or include wafer-scale systematic gradients.

## Stability, startup, retention, and noise

Middlebrook voltage injection at the extracted buffer feedback gate tests 120 combinations: five corners, both supply boundaries, both temperature boundaries, three input voltages, two loads. Minimum phase margin is {summary['min_phase_margin_deg']:.2f}°; all exceed the 60° criterion.

![Stability and step responses](../docs/images/stability_settling.png)

Startup from zero stored charge, a 10 µs supply ramp, references established by 15 µs, and conversion starting at 20 µs passes the half-LSB raw-error check at nominal conditions. Three standalone buffer conditions test full-range steps. Worst half-LSB settling is {settling:.2f} µs; worst overshoot is {summary['max_buffer_overshoot_mv']:.1f} mV. Allow 8 µs for full-range standalone buffer steps. Actual DAC conversion timing is separately tested by the complete code sweeps.

Four hot hold cases keep the sample bank at the opposite reference for almost 100 µs. Immediate sample-to-hold feedthrough reaches {summary['max_opposite_sample_kick_lsb']:.4f} LSB. Subsequent 50 µs drift is at most {summary['max_hold_drift_50us_lsb']:.5f} LSB, below the 0.1 LSB retention criterion. Refresh periodically; changing the sample bank disturbs the held voltage.

Continuous-time buffer noise integrated from 0.1 Hz to the 10.66 kHz conversion Nyquist frequency spans {summary['buffer_noise_uv_rms_range'][0]:.1f}–{summary['buffer_noise_uv_rms_range'][1]:.1f} µV RMS in three cases. Estimated kT/C for 6.454 pF at 85 °C is 27.7 µV RMS. Sampled switching noise, distortion, and measured ENOB remain uncharacterized. Peak simulated conversion supply current is {summary['max_supply_current_ua']:.1f} µA; peak reference current is {summary['max_reference_current_ma']:.3f} mA.

## Physical and numerical verification

Exact area is 20,700 µm², {summary['area_reduction_from_source_pct']:.2f}% smaller than the source macro. All manufacturing polygons fit the boundary on a 5 nm grid. M4 power rails are vertical; M5 power rails are horizontal. All eight LEF interface rectangles exist on the corresponding GDS metal/pin layers. Two analog inputs and one analog output are within the call's analog limits; allocation of three digital phase inputs remains unconfirmed. Full DRC, native/GDS LVS, antenna reports, and geometry audit are attached. The KiCad schematic has zero ERC messages, 72 checked visible connections, and 26 verified device-property sets. MOS bodies are explicit in silicon and SPICE; their supply ties are recorded as schematic properties.

Full RC and coupled-capacitance extraction come from the delivered GDS using the fixed IIC OSIC image. Resistance threshold/minimum: 1 Ω; delay cutoff: zero. Exact star-mesh reduction removes only capacitance-free resistor nodes and preserves device/port/capacitive nodes. Raw/reduced RC, cached/full models, and 100 ns/25 ns time-step comparisons agree within 10 µV at four representative codes. Repeating a mismatch seed reproduces identical results. Detailed differences are in `signoff/special_results.json`; this supports the tested numerical approximations without proving all possible transient behavior.

A fresh build reproduces the schematic SPICE and every GDS polygon. GDS timestamps may differ. Resistor URPM mask hints must be preserved on GDS import (`gds maskhints yes`). These checks use the installed open SKY130 rules; final organizer chip-integration checks are separate.

Final GDS SHA-256: `{sha}`. Final reduced RC SHA-256: `{rcsha}`. Every simulation result is audited against these hashes. `all_code_results.csv` contains all complete sweeps; JSON, simulation decks, logs, model files, native cells, and generators support reproduction. Compact packages omit redundant DUT snapshots and per-run waveform vectors; generators regenerate them. Recorded special waveforms support the included settling plots.

## Submission scope

The [supplied call](../requirements/Silicluster_v3_full_call_for_participation.pdf), pages 2–3, defines the size, analog I/O limits, required files, and M4/M5 grid. It gives digital-project I/O separately, without assigning digital controls to analog projects or a physical pin template. See [the requirements checklist](../docs/submission.md) and [organizer questions](../docs/organizer_questions.md). This macro includes no padframe, ESD cells, package model, or on-chip sequencer. No submission email has been sent.
'''
(V/'verification.md').write_text(report,encoding='utf-8')
print(json.dumps(summary,indent=2))
