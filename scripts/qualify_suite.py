"""Run independent extracted-layout qualification cases with bounded concurrency."""
from pathlib import Path
import argparse, concurrent.futures, itertools, json, subprocess, sys, time
P=Path(__file__).resolve().parents[1]
S=P/'scripts'; Q=P/'verification/signoff'
ap=argparse.ArgumentParser();ap.add_argument('suite',choices=['ac','pvt','full','mc']);ap.add_argument('--jobs',type=int,default=4);a=ap.parse_args()
rc=str(P/'netlist/silicluster_jonah_2cap_dac.rc.spice')
jobs=[]
if a.suite=='ac':
    for corner,supply,temp,load,vin in itertools.product(['tt','ss','ff','sf','fs'],[1.62,1.98],[-40,85],[5,20],[.2,.55,.9]):
        jobs.append([sys.executable,str(S/'buffer_ac.py'),'--corner',corner,'--supply',str(supply),'--temp',str(temp),'--load',str(load),'--vin',str(vin),'--netlist',rc])
elif a.suite=='pvt':
    for i,(corner,supply,temp) in enumerate(itertools.product(['tt','ss','ff','sf','fs'],[1.62,1.98],[-40,27,85])):
        jobs.append([sys.executable,str(S/'qualify.py'),'probe','--name',f'pvt_{i:02d}','--corner',corner,'--supply',str(supply),'--temp',str(temp),'--load','20','--netlist',rc])
elif a.suite=='full':
    from qualify import transient,metrics
    configs=[(f'full_{c}',c,1.8,27,5,None) for c in ['tt','ss','ff','sf','fs']]
    pvt=[json.loads((Q/f'pvt_{i:02d}_result.json').read_text()) for i in range(30)]
    mc=[json.loads((Q/f'mc_{i}_result.json').read_text()) for i in range(1001,1033)]
    for name,r in [('full_worst_inl',max(pvt,key=lambda r:r['selected_endpoint_inl_lsb'])),
                   ('full_worst_dnl',max(pvt,key=lambda r:max(abs(r['selected_min_dnl_lsb']),abs(r['selected_max_dnl_lsb'])))),
                   ('full_mc_inl',max(mc,key=lambda r:r['selected_endpoint_inl_lsb'])),
                   ('full_mc_raw',max(mc,key=lambda r:r['max_raw_error_lsb']))]:
        configs.append((name,r['corner'],r['supply_v'],r['temp_c'],r['load_pf'],r['mismatch_seed']))
    (Q/'full_configs.json').write_text(json.dumps(configs,indent=2)+'\n')
    for name,corner,supply,temp,load,seed in configs:
        for start in range(0,256,8):
            n=name+f'_block{start:03d}'
            transient(n,list(range(start,start+8)),corner,supply,temp,load,100,seed,rc)
            jobs.append([sys.executable,str(S/'qualify.py'),'run','--name',n])
elif a.suite=='mc':
    for seed in range(1001,1033):
        jobs.append([sys.executable,str(S/'qualify.py'),'probe','--name',f'mc_{seed}','--seed',str(seed),'--netlist',rc])
def run(cmd):
    start=time.time(); r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(' '.join(cmd)+'\n'+r.stdout+'\n'+r.stderr)
    print(f'{a.suite}: completed {cmd[3:]} in {time.time()-start:.1f}s',flush=True)
    return {'command':cmd,'seconds':time.time()-start,'returncode':r.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
    results=list(pool.map(run,jobs))
(Q/(a.suite+'_suite.json')).write_text(json.dumps(results,indent=2)+'\n')
if a.suite=='full':
    for name,*_ in configs:
        parts=[json.loads((Q/(name+f'_block{start:03d}_result.json')).read_text()) for start in range(0,256,8)]
        rows=[{**r,'block':part['name']} for part in parts for r in part['rows']]
        result=metrics({**parts[0],'name':name,'block_count':32,'block_method':'8 ascending codes per run; every code initialized for 8us'},rows,max(p['max_supply_current_ua'] for p in parts),max(p['max_reference_current_ma'] for p in parts))
        (Q/(name+'_result.json')).write_text(json.dumps(result,indent=2)+'\n')
print(f'{a.suite}: {len(results)} cases completed',flush=True)
