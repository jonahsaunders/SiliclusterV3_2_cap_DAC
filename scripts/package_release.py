"""Create a portable Silicluster submission ZIP with verified member hashes."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,zipfile
P=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args()
workspace=P.parent.parent if P.parent.name=='work' else P.parent
out=(a.output or workspace/'outputs').resolve();out.mkdir(parents=True,exist_ok=True)
subprocess.run([sys.executable,str(P/'scripts/release_report.py')],check=True)
s=json.loads((P/'verification/summary.json').read_text())
Q=P/'verification/signoff'
# Testbench copies are electrically identical to the recorded source; replace
# their include paths before omitting the redundant snapshots from the ZIP.
for case in Q.glob('*_case.json'):
    c=json.loads(case.read_text());deck=Q/(case.name[:-10]+'.spice')
    if not deck.exists():continue
    target=P/'netlist'/Path(c['netlist']).name
    assert target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==c['netlist_sha256'],case
    text=deck.read_text()
    text=re.sub(r'(?m)^\.include [^\n]*'+re.escape(case.name[:-10])+r'_dut\.spice$',
                '.include netlist/'+target.name,text)
    deck.write_text(text)
for directory in [P/'sim',Q]:
    for deck in directory.glob('*.spice'):
        if deck.name.endswith('_dut.spice'):continue
        deck.write_text(deck.read_text().replace(str(P)+'/', ''))

def include(file):
    rel=file.relative_to(P)
    if any(part in {'.git','build','__pycache__'} for part in rel.parts):return False
    if file.name=='manifest.json' or file.suffix in {'.pyc','.zip'}:return False
    if rel.parts[:2]==('verification','signoff'):
        if file.name.startswith('ci_probe') or file.name.endswith('_dut.spice'):return False
        if file.suffix=='.txt' and not file.name.startswith(('step_','powerup','hold_','noise_')):return False
    return True
paths=[p for p in sorted(P.rglob('*')) if p.is_file() and include(p)]
manifest={'project':'Silicluster v3 two-capacitor DAC','status':s['status'],'gds_sha256':s['gds_sha256'],
    'rc_sha256':s['rc_sha256'],'files':[{'path':f.relative_to(P).as_posix(),'bytes':f.stat().st_size,
        'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in paths],
    'excluded':'Git/build/cache directories, repeated DUT copies and per-run raw vectors; simulation generators reproduce them',
    'testbench_working_directory':'Repository root; saved deck paths are relative except optional installed full-PDK comparison',
    'pending':['Organizer approval of digital controls on analog slot','Final analog pin and PDN integration template','Participant city']}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
zip_path=out/'silicluster_v3_2cap_dac.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in paths+[P/'manifest.json']:z.write(f,arcname='silicluster_dac/'+f.relative_to(P).as_posix())
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    for record in manifest['files']:
        assert hashlib.sha256(z.read('silicluster_dac/'+record['path'])).hexdigest()==record['sha256']
# Expose only user-facing deliverables in the workspace outputs directory.
deliver=out/'silicluster_dac';deliver.mkdir(exist_ok=True)
for source,target in [(P/'verification/silicluster_validation.pdf','silicluster_validation.pdf'),
                      (P/'schematic/suarez_dac.pdf','schematic.pdf')]:
    if source.exists():shutil.copyfile(source,deliver/target)
for name in ['layout_overview.png','schematic_overview.png','linearity.png','stability_settling.png','timing.png']:
    shutil.copyfile(P/'docs/images'/name,deliver/name)
print(json.dumps({'zip':str(zip_path),'bytes':zip_path.stat().st_size,'files':len(paths)+1,
                  'gds_sha256':s['gds_sha256'],'all_member_hashes_verified':True},indent=2))
