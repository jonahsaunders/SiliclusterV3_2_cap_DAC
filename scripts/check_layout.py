"""Audit the delivered geometry and eight-port scalar interface against the v3 call."""
from pathlib import Path
import json, re, hashlib
import klayout.db as db
import numpy as np

P=Path(__file__).resolve().parents[1]; TOP='silicluster_jonah_2cap_dac'
ly=db.Layout(); ly.read(str(P/f'gds/{TOP}.gds')); top=ly.top_cell()
bbox=top.dbbox()
assert top.name==TOP and [bbox.left,bbox.bottom,bbox.right,bbox.top]==[0,0,180,115]
for li in ly.layer_infos():
    if li.datatype==5:continue  # Text is annotation, not a manufacturing polygon.
    r=db.Region(top.begin_shapes_rec(ly.layer(li)))
    assert (r-db.Region(db.Box(0,0,round(180/ly.dbu),round(115/ly.dbu)))).is_empty(),li
    for poly in r.each():
        assert all(abs(round(v*ly.dbu/.005)-v*ly.dbu/.005)<1e-7 for q in poly.each_point_hull() for v in [q.x,q.y]),li
placement=json.loads((P/'layout/placement.json').read_text()); banks={}
for name in ['SAMPLE','HOLD']:
    units=[c for c in placement['capacitors'] if c['bank']==name]
    banks[name]={'units':len(units),'centroid_um':np.mean([[c['x'],c['y']] for c in units],axis=0).tolist()}
    assert len(units)==16
assert np.allclose(banks['SAMPLE']['centroid_um'],banks['HOLD']['centroid_um'],atol=1e-10)
m4=db.Region(top.begin_shapes_rec(ly.layer(71,20)))
m5=db.Region(top.begin_shapes_rec(ly.layer(72,20)))
assert not m5.is_empty()
for x in [2,178]:
    assert (db.Region(db.Box(round((x-.6)/ly.dbu),0,round((x+.6)/ly.dbu),round(115/ly.dbu)))-m4).is_empty()
for y in [1.5,113.5]:
    assert (db.Region(db.Box(0,round((y-.8)/ly.dbu),round(180/ly.dbu),round((y+.8)/ly.dbu)))-m5).is_empty()
lef=(P/f'lef/{TOP}.lef').read_text()
ports=json.loads((P/'design.json').read_text())['ports']
assert re.search(r'SIZE 180\.000 BY 115\.000',lef)
assert re.findall(r'^  PIN (\S+)',lef,re.M)==ports
verilog=(P/'src/project.v').read_text()
assert set(re.findall(r'(?:input|output) wire (\w+)',verilog))==set(ports)
pinlayer=db.Region(top.begin_shapes_rec(ly.layer(71,16)))
for name in ports:
    section=re.search(r'  PIN '+name+r'\n(.*?)  END '+name,lef,re.S)[1]
    xy=list(map(float,re.search(r'RECT ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)',section).groups()))
    rect=db.Region(db.Box(*[round(v/ly.dbu) for v in xy]))
    assert (rect-m4).is_empty() and (rect-pinlayer).is_empty(),name
    assert ('DIRECTION OUTPUT' in section)==(name=='vout'),name
for filename,suffix in [('extracted_lvs.spice',''),('gds_lvs.spice','_flat')]:
    text=re.sub(r'\n\+',' ',(P/'netlist'/filename).read_text())
    actual=next(s.split()[2:] for s in text.splitlines() if s.lower().startswith('.subckt '+TOP+suffix+' '))
    assert set(actual)==set(ports),(filename,actual)
urpm=[]
for cell in ly.each_cell():
    if cell.name.startswith('dev_res'):
        r=db.Region(cell.begin_shapes_rec(ly.layer(79,20)))
        urpm.append({'cell':cell.name,'width_um':r.bbox().width()*ly.dbu})
assert urpm and all(r['width_um']>=1.27 for r in urpm)
report={'macro_um':[180,115],'area_um2':20700,'bbox_um':[bbox.left,bbox.bottom,bbox.right,bbox.top],
    'metal5_present':True,'power_grid':'vertical M4, horizontal M5','manufacturing_grid_um':.005,
    'capacitor_banks':banks,'resistor_implants':urpm,'interface_ports':ports,
    'pin_rectangles_verified_in_gds_and_lef':8,'analog_inputs':2,'analog_outputs':1,'digital_control_inputs':3,
    'integration_status':'Organizer must confirm digital phase pins for an analog slot and final pin locations',
    'gds_sha256':hashlib.sha256((P/f'gds/{TOP}.gds').read_bytes()).hexdigest()}
(P/'verification/layout_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
