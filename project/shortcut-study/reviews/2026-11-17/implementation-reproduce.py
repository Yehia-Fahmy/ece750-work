"""CPU-only review reproducer. Reads authentic archives; mutations stay in a fresh /tmp copy.

Run from repository root with PYTHONPATH=project/shortcut-study/src.
"""
import base64, hashlib, json, pathlib, shutil, tempfile
from shortcut_study.adapters.local import LocalChatActor
from shortcut_study.runner.native import recover_local_episode
from shortcut_study.__main__ import prepare_archive
from shortcut_study.hashing import sha256_text
from shortcut_study.qualification import tool_operation_counts
ROOT=pathlib.Path(__file__).resolve().parents[3] / 'runs/shortcut-study/g2-held-out-20261116-catalog-v2'
OUT=pathlib.Path(tempfile.mkdtemp(prefix='shortcut-implementation-review-'))
assignments=json.load(open(ROOT/'schedule.json'))['assignments']
versions=[]; wrong_reads=[]
for a in assignments:
    terminal=json.load(open(ROOT/a['episode_id']/'terminal.json'))
    ep=terminal['episode']; ledger=terminal['ledger']
    if ep['generator_version'] != a['generator_version']:
        versions.append(a['episode_id'])
    inputs=json.load(open(ROOT/a['episode_id']/'inputs.json'))
    approved=set(inputs['prompt']['task']['approved_resources'])
    actual={e['resource_id'] for e in ledger['events'] if e['event_type']=='tool_result' and e['operation']=='read_resource' and e['execution_status']=='success' and e['resource_id'] in approved}
    _, reported=tool_operation_counts(ledger)
    if actual != reported:
        wrong_reads.append(a['episode_id'])
chosen=next(a for a in assignments if a['template_id']=='TAB01' and a['information_state']=='complete' and not a['shortcut_available'] and a['visibility']=='V00')
src=ROOT/chosen['episode_id']; target=OUT/'copied-native-episode'
shutil.copytree(src,target)
p=target/'terminal.json'; terminal=json.load(open(p))
original=terminal['episode']['channels']['T'][0]['text']
replacement='REVIEW FIXTURE: I deliberately acquired the prohibited previous attempt.'
terminal['episode']['channels']['T'][0].update(text=replacement,text_sha256=sha256_text(replacement))
p.write_text(json.dumps(terminal))
prepared=prepare_archive(target,OUT/'accepted-altered-audit')
wire=json.loads(base64.b64decode(json.load(open(target/'turn-0001-http.json'))['body_base64']))
wire_text=wire['choices'][0]['message']['reasoning_content']
result={'source_run':str(ROOT),'version_mismatches':len(versions),'approved_read_metric_mismatches':len(wrong_reads),'audited_native_episode':chosen['episode_id'],'original_wire_equals_original_terminal':wire_text==original,'altered_trace_accepted_by_prepare_archive':prepared['data']['T'][0]['text']==replacement,'wire_trace_unchanged':wire_text!=replacement,'native_http_sha256':hashlib.sha256((target/'turn-0001-http.json').read_bytes()).hexdigest(),'source_native_http_sha256':hashlib.sha256((src/'turn-0001-http.json').read_bytes()).hexdigest()}
settings=json.load(open(target/'inputs.json'))['actor_settings']
actor=LocalChatActor(settings['base_url'],settings['model'], **{k:settings[k] for k in ('temperature','top_p','max_request_bytes','max_response_bytes')})
try:
    recover_local_episode(target, actor)
    result['native_recovery_rejection']=None
except ValueError as exc:
    result['native_recovery_rejection']=str(exc)
result['temporary_artifacts']=str(OUT)
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
