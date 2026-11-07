"""Prepare reduced main manifest without resampling reserved questions."""
import argparse
from pathlib import Path
from observer_study.io import read_json, digest, write_json
from observer_study.experiment import schedule

def prepare(config, reserved):
    if config['conditions'] != ['C0', 'C1', 'D-R', 'D-A']:
        raise ValueError('Reduced design requires prespecified developer arms')
    selected = []
    for task in config['tasks']:
        candidates = [i for i in reserved['items'] if i['task']==task and i['split']=='main']
        if len(candidates) != 40:
            raise ValueError('Expected 40 previously reserved main items per task')
        selected.extend(candidates[:20])
    result = {**reserved, 'config_sha256':digest(config), 'items':selected,
              'selection':{'rule':'first 20 per task in original seeded main reservation order',
                           'reserved_manifest_sha256':digest(reserved),
                           'unselected_main_items':60}}
    if len(schedule(config,result,'main')) != 240:
        raise ValueError('Expected 240 requests')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--reserved',type=Path,default=Path('project/data/items-pilot-v1.json'))
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    result=prepare(read_json(a.config),read_json(a.reserved))
    if a.out.exists(): raise ValueError('Choose fresh manifest path')
    write_json(a.out,result)
if __name__=='__main__': main()
