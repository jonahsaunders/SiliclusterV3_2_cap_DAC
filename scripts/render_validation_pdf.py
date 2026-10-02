"""Produce a compact, printable companion to verification/verification.md."""
from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT

P=Path(__file__).resolve().parents[1];s=json.loads((P/'verification/summary.json').read_text())
W,H=A4;content=W-84
style=getSampleStyleSheet()
style.add(ParagraphStyle(name='Main',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=10,textColor=colors.HexColor('#233347')))
style.add(ParagraphStyle(name='SmallText',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=8,textColor=colors.HexColor('#46566a')))
style['Title'].fontName='Helvetica-Bold';style['Title'].fontSize=24;style['Title'].leading=28
style['Heading1'].textColor=colors.HexColor('#007d81');style['Heading1'].fontSize=17;style['Heading1'].spaceAfter=13
story=[]
def para(text,small=False):story.append(Paragraph(text,style['SmallText' if small else 'Main']))
def heading(text):story.append(Paragraph(text,style['Heading1']))
def figure(name,maxheight=400):
    from PIL import Image as PILImage
    path=P/'docs/images'/name
    with PILImage.open(path) as im:w,h=im.size
    scale=min(content/w,maxheight/h)
    story.append(Image(str(path),width=w*scale,height=h*scale));story.append(Spacer(1,12))
def table(rows,widths=None):
    t=Table(rows,colWidths=widths or [content*.51,content*.49],hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#007d81')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),
        ('LEADING',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef4f5'),colors.white]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#bacbd2'))]))
    story.append(t);story.append(Spacer(1,14))
story.append(Paragraph('Silicluster v3<br/>Two-capacitor serial DAC',style['Title']))
para('Simulation and validation companion | October 2, 2026 | Jonah Saunders, independent designer, United States')
para('<b>Prepared physical macro; organizer interface confirmation remains open.</b> The 180 x 115 um SKY130 cell passes local physical and circuit checks. Three digital phase inputs for an analog slot, final signal pins, and power-grid landings still need organizer confirmation. No submission, acceptance, fabrication, or measured silicon is claimed.')
table([['Final-layout check','Result'],['Size / area','180 x 115 um / 20,700 um2'],
    ['Area reduction from source',f"{s['area_reduction_from_source_pct']:.2f}%"],['Full DRC / antenna','0 violations / 0 feedback'],
    ['Native and re-imported GDS LVS','Unique match; no property errors'],['Schematic ERC / visible connections','0 violations / 72 checked'],
    ['Complete code sweeps','9 x 256; all strictly monotonic'],['Worst endpoint INL',f"{s['worst_full_endpoint_inl_lsb']:.4f} LSB"],
    ['DNL range',f"{s['min_full_dnl_lsb']:.4f} to {s['max_full_dnl_lsb']:.4f} LSB"],
    ['Stability cases / minimum margin',f"120 / {s['min_phase_margin_deg']:.2f} degrees"],
    ['PVT probe points / mismatch seeds','30 / 32']])
para('Qualified assumptions: 1.8 V nominal supply; boundaries 1.62/1.98 V; five process corners; -40/27/85 C samples; fixed 0.2/0.9 V references; 5-20 pF load with 10 Mohm DC impedance. Assumed analog paths include 500 ohm series resistance and 5 pF on reference inputs. These are test fixtures, not confirmed organizer pad models.')
para('Endpoint INL removes offset and gain. Accurate absolute voltage requires calibration. Discrete model-based tests do not establish silicon yield, ENOB, or final chip integration performance.',True)
story.append(PageBreak());heading('Circuit and compact floorplan')
figure('layout_overview.png',440)
para('The conversion core shares charge between two nominally 6.454 pF banks, each sixteen 14 x 14 um MIM units. Their common centroids are (72.75, 43.00) um. Ground shields separate sample/hold routing. Twenty MOS transistors implement phase inversion, switching, bias, and a unity-gain output buffer. A separate 1.373 pF C3 capacitor compensates that buffer.')
para('Device sizes and conversion capacitance are preserved from the source circuit. The native KiCad schematic and PDF are supplied separately for detailed reading. All MOS bulk ties are explicit in SPICE and silicon. Vertical M4 power rails and horizontal M5 rails implement the call\'s grid orientation; all geometry is inside the declared boundary on a 5 nm grid.')
para('Interface: VGND, VDPWR, charge_high, charge_low, share, vref_high, vref_low, vout. Signal pins are provisional M4 rectangles. The call grants two analog inputs and two analog outputs, but does not explicitly allocate digital controls to analog projects.',True)
story.append(PageBreak());heading('Transfer, linearity, and mismatch')
figure('linearity.png',430)
para('Five full sweeps cover nominal supply and temperature at TT, SS, FF, SF, and FS. Two additional full sweeps use PVT probe conditions with the highest observed selected-code INL/DNL; two use mismatch seeds with the highest observed selected-code INL/raw error. Selection comes from this layout\'s results and is recorded in full_configs.json. These are sampled stress cases, not an exhaustive worst-case search.')
para(f"Across all nine sweeps, worst endpoint INL is {s['worst_full_endpoint_inl_lsb']:.4f} LSB. Thirty PVT points and 32 local-mismatch seeds also pass selected-code monotonicity. Mismatch endpoint offset spans {s['mc_offset_range_mv'][0]:.2f} to {s['mc_offset_range_mv'][1]:.2f} mV. Calibrate codes 0 and 255 to remove measured endpoint offset/gain; residual nonlinear error remains.")
para('Each measured code begins with the same initialization. Eight codes are grouped per run. All 2,304 complete-sweep measurements are supplied in all_code_results.csv with detailed case JSON and simulator logs. Local mismatch sampling excludes wafer-scale systematic capacitor gradients and package variation.',True)
story.append(PageBreak());heading('Timing, stability, and retention')
figure('stability_settling.png',225);figure('timing.png',215)
para(f"All 120 buffer feedback-injection cases exceed 60 degrees phase margin; the minimum is {s['min_phase_margin_deg']:.2f} degrees. Worst full-range standalone buffer settling is {s['max_buffer_settling_0p5lsb_us']:.2f} us to half an LSB; allow 8 us. Worst overshoot is {s['max_buffer_overshoot_mv']:.1f} mV. The actual DAC read timing is tested separately by complete conversion sweeps.")
para(f"Hot hold cases show up to {s['max_opposite_sample_kick_lsb']:.4f} LSB of immediate feedthrough when the sample bank changes to the opposite reference, followed by at most {s['max_hold_drift_50us_lsb']:.5f} LSB drift over 50 us. Refresh periodically. Integrated modeled buffer noise is {s['buffer_noise_uv_rms_range'][0]:.1f}-{s['buffer_noise_uv_rms_range'][1]:.1f} uV RMS over 0.1 Hz-10.66 kHz; kT/C at 85 C is estimated at 27.7 uV RMS. These are not measured ENOB results.",True)
story.append(PageBreak());heading('Evidence, reproduction, and submission')
para('Physical evidence includes native layout DRC, full DRC after independent GDS re-import, antenna checks, and native/re-imported transistor-level LVS. The geometry audit checks bounds, manufacturing grid, capacitor centroids, and all eight GDS/LEF pin rectangles. A fresh build reproduces the circuit and all GDS polygons. Preserve resistor URPM mask hints when importing GDS.')
para('Coupled-C and full RC extraction use the pinned IIC OSIC Tools 2026.07 image with SKY130A. Resistance threshold/minimum is 1 ohm and delay cutoff is zero. Exact reduction removes only capacitance-free resistor nodes. Raw/reduced RC, cached/full models, and 100 ns/25 ns maximum time steps agree within 10 uV at four representative codes. Repeating a mismatch seed gives identical output. Source/model/result hashes are audited before reporting.')
para('Reproduce from the repository root with the pinned image and bash scripts/verify.sh. The --smoke variant runs physical checks, a fresh build, and a ten-code extracted transfer probe. Full qualification regenerates all sweeps and reports. See docs/reproduce.md for Docker and native KiCad commands. The complete narrative validation document is verification/verification.md.')
para('<b>Package:</b> final GDS, Magic top and child cells, LEF, external-interface Verilog, editable schematic, reference and extracted netlists, testbenches, PDK model cache and license, simulator results/logs, DRC/LVS evidence, figures, generators, and a hash manifest. Redundant raw waveform vectors and DUT snapshots are regenerated by scripts.')
para('<b>Remaining integration work:</b> obtain organizer approval for three digital phase inputs on an analog slot and the physical pin/power-rail template. Incorporate any required changes and rerun checks. Fill the participant city before sending the prepared submission email with the current ZIP. Country is United States and affiliation is independent designer. No email has been sent.')
para('The supplied Silicluster v3 full call, sections 8-11 and 16, defines the analog I/O limits, size, required ZIP contents, grid orientation, and participant information. It gives a deadline of October 31, 2026, 11:59 p.m. Mexico City time, subject to remaining slots and compliance. Acceptance does not guarantee a packaged chip. The call PDF is included under requirements/.',True)
para('Repository: https://github.com/jonahsaunders/SiliclusterV3_2_cap_DAC',True)
para('GDS SHA-256: '+s['gds_sha256'][:32]+'<br/>'+s['gds_sha256'][32:],True)
para('Reduced RC SHA-256: '+s['rc_sha256'][:32]+'<br/>'+s['rc_sha256'][32:],True)
def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#58677a'))
    canvas.drawString(42,25,'Silicluster v3 two-capacitor DAC | Model-based validation')
    canvas.drawRightString(W-42,25,str(doc.page))
SimpleDocTemplate(str(P/'verification/silicluster_validation.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=40,bottomMargin=44).build(story,onFirstPage=footer,onLaterPages=footer)
print('Created printable validation companion.')
