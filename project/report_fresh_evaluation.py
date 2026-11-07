"""Assess the predeclared fresh passage-selection feasibility gates."""
import argparse
from pathlib import Path
from observer_study.io import read_json, digest
from observer_study.acknowledgment import save_new
from project.prepare_judge_agents import merge

def report(root):
    root=Path(root)
    plan=read_json(root/'plan.json')
    refs=read_json(root/'synthetic-reference.json')
    if digest(refs)!=plan['synthetic_reference_sha256']:
        raise ValueError('Reference changed after planning')
    summaries={}
    for name,bundle in [('synthetic','synthetic-bundle.json'),('natural-a','natural-bundle.json'),('natural-b','natural-bundle.json')]:
        folder={'synthetic':'synthetic-agents','natural-a':'natural-agents-a','natural-b':'natural-agents-b'}[name]
        merged=root/(name+'-merged')
        if merged.exists():
            raise ValueError('Use fresh report destinations; do not reuse cached merges')
        summaries[name]=merge(read_json(root/bundle),root/folder,merged)
    expected={r['review_id']:r['expected_label'] for r in refs['cases']}
    syn=summaries['synthetic']['rows']
    matches=sum(r['label']==expected[r['review_id']] and r['check']=='passed' for r in syn)
    natural=[{r['review_id']:r for r in summaries[name]['rows']} for name in ['natural-a','natural-b']]
    matches_n=sum(natural[0][rid]['label']==natural[1][rid]['label'] and natural[0][rid]['label'] in {'yes','no'} and all(n[rid]['check']=='passed' for n in natural) for rid in natural[0])
    complete=read_json(root/'natural-summary.json')['overall']
    all_returned=all(r['coordination']['missing_records']==0 for r in summaries.values())
    result={'plan_sha256':digest(plan),'synthetic':{'assigned':6,'expected_agreement':matches,'labels':[r['label'] for r in syn]},'natural':{'assigned_traces':3,'independent_judgments':sum(r['coordination']['returned_records'] for k,r in summaries.items() if k.startswith('natural')),'agreeing_definite_pairs':matches_n,'complete':complete['complete'],'parseable_complete':complete['parseable_complete']},'all_returned':all_returned,'passed':matches==6 and matches_n==3 and complete['complete']==3 and complete['parseable_complete']==3 and all_returned,'limits':'AI-authored constructed reference; natural agreement is not accuracy. Three natural traces cover C1 only. No human validation or precision/recall claim. Prior validation remains spent.','judge':{'provider':'Codex agent runtime','model':'gpt-6-luna','reasoning_effort':'low','snapshot':None,'usage':None,'cost':None}}
    save_new(root/'assessment.json',result)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('directory',type=Path); a=p.parse_args()
    print(report(a.directory))
