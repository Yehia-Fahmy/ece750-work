"""Read-only postcollection verification of the frozen main run and raw scoring."""
import argparse
import json
from pathlib import Path
from observer_study.io import read_json, digest, file_digest
from observer_study.runner import source_hash
from observer_study.scoring import score_response, unknown_score
from observer_study.acknowledgment import save_new

def audit(directory, freeze_path):
    directory=Path(directory)
    manifest=read_json(directory/'manifest.json')
    freeze=read_json(freeze_path)
    identity=manifest['identity']
    if identity['split']!='main' or identity['dry_run']:
        raise ValueError('Expected real main run')
    if source_hash()!=freeze['source_sha256'] or identity['source_sha256']!=freeze['source_sha256']:
        raise ValueError('Source differs from frozen collection')
    for path, expected in freeze['files'].items():
        if file_digest(path)!=expected:
            raise ValueError('Frozen file changed: '+path)
    if digest(identity['config'])!=freeze['main_config_sha256']:
        raise ValueError('Config changed')
    if identity['prepared_sha256']!=freeze['main_items_sha256']:
        raise ValueError('Prepared manifest changed')
    if digest(manifest['requests'])!=identity['requests_sha256']:
        raise ValueError('Schedule changed')
    expected_ids={r['request_id'] for r in manifest['requests']}
    if len(expected_ids)!=240 or {p.stem for p in (directory/'responses').glob('*.json')}!=expected_ids:
        raise ValueError('Response file coverage differs from 240 assigned requests')
    checked=0; terminal_failures=[]; retries=0; changed=[]
    for request in manifest['requests']:
        rid=request['request_id']; record=read_json(directory/'responses'/(rid+'.json'))
        if record['request_id']!=rid or record['status'] not in {'returned','technical_error','interrupted'}:
            raise ValueError('Pending or mismatched response: '+rid)
        attempts=record['attempts']; retries+=max(0,len(attempts)-1)
        if len(attempts)>identity['config']['technical_retries']+1:
            raise ValueError('Too many attempts')
        for attempt in attempts[:-1]:
            if attempt.get('retryable') is not True:
                raise ValueError('Retry without transient failure')
        if record['status']=='returned':
            attempt=attempts[-1]
            if json.loads(attempt['raw_body'])!=attempt['response']:
                raise ValueError('Raw body mismatch: '+rid)
            score=score_response(attempt['response'],request['item']);checked+=1
        else:
            score=unknown_score();terminal_failures.append(rid)
        if score!=record['score']: changed.append(rid)
    if changed: raise ValueError('Rescoring changed saved scores: '+str(changed))
    return {'run':str(directory),'assigned':240,'raw_responses_audited':checked,'terminal_failure_ids':terminal_failures,'technical_retries':retries,'changed_scores':changed,'freeze_files_verified':len(freeze['files']),'source_sha256':source_hash(),'audit_script_sha256':file_digest(__file__),'source_manifest_sha256':digest(manifest),'passed':True}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);p.add_argument('--freeze',type=Path,default=Path('project/results/main-reduced-v1-freeze.json'));p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=audit(a.run,a.freeze);save_new(a.out,result);print(result)
