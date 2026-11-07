"""Export completed frozen main traces to single-trace packets without labeling them.

This postcollection exporter does not modify the frozen generation/analysis package.
"""
import argparse
import json
from pathlib import Path
from observer_study.acknowledgment import VERSION, RUBRIC, PATTERN, baseline, save_new
from observer_study.io import digest, read_json
from observer_study.summary import run_records
from prepare_judge_agents import prepare
from audit_main import audit

def export(run, freeze, output):
    verified=audit(run,freeze)
    manifest,records=run_records(run)
    entries=[]
    for request,response in records:
        score=response['score']
        excluded=('no_hint' if not request['hint_present'] else
                  'incomplete_trace' if not score['complete'] or not score['reasoning'].strip() else None)
        state={'question':request['item']['question'],
               'suggestion':f"({request['item']['wrong_hint']})" if request['hint_present'] else None,
               'reasoning':score['reasoning']}
        entries.append({'review_id':digest(request['request_id'])[:16],
                        'request_id':request['request_id'],'condition':request['condition'],
                        'task':request['item']['task'],'input_sha256':digest(state),
                        'excluded_reason':excluded,'baseline':baseline(state['reasoning']),
                        'messages':[{'role':'system','content':RUBRIC},
                                    {'role':'user','content':json.dumps(state,ensure_ascii=False)}]})
    bundle={'schema_version':1,'version':VERSION,'rubric':RUBRIC,'baseline_pattern':PATTERN,
            'source_kind':'frozen_main_postcollection_export','source_manifest_sha256':digest(manifest),
            'source_records_sha256':digest(records),'freeze_sha256':digest(read_json(freeze)),
            'entries':entries}
    bundle['bundle_sha256']=digest(bundle)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    save_new(output/'bundle.json',bundle)
    index=prepare(bundle,output/'agents')
    save_new(output/'export-audit.json',{'raw_audit':verified,'eligible':index['eligible'],
             'assigned':len(entries),'excluded_no_hint':sum(e['excluded_reason']=='no_hint' for e in entries),
             'excluded_incomplete':sum(e['excluded_reason']=='incomplete_trace' for e in entries),
             'labels_created':0,'limitation':'Packets are prepared only; main acknowledgment labels and researcher validation remain pending.'})
    return index
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path)
    p.add_argument('--freeze',type=Path,default=Path('project/results/main-reduced-v1-freeze.json'))
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    r=export(a.run,a.freeze,a.out);print(f"Prepared {r['eligible']} single-trace packets; no labels created")
