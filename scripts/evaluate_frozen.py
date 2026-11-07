"""Compute metrics only from explicitly supplied human labeling files."""
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.editorial_policy import ordering

def metrics(cases,predictions,labels=(),pairs=()):
    allowed={x['candidate']['id'] for x in cases};rows=list(labels);pairs=list(pairs)
    accepted=[]
    for row in rows:
        if not row.get('human_accept'):continue
        if row['candidate_id'] not in allowed or row['human_accept'] not in ('yes','no') or not row.get('reviewer','').strip():raise ValueError('Labels require known IDs, yes/no and human reviewer attribution')
        accepted.append(row)
    if len({r['candidate_id'] for r in accepted})!=len(accepted):raise ValueError('Duplicate labels')
    selected=[r for r in accepted if predictions[r['candidate_id']]['decision']['eligible']]
    ordered=sorted(predictions.values(),key=ordering);ranks={x['id']:i for i,x in enumerate(ordered)}
    agreements=[]
    for row in pairs:
        if not row.get('preferred'):continue
        a,b=row['candidate_a'],row['candidate_b'];p=row['preferred']
        if a==b or a not in allowed or b not in allowed or p not in (a,b,'tie') or not row.get('reviewer','').strip():raise ValueError('Invalid human pair label')
        if p!='tie':agreements.append((ranks[a]<ranks[b])==(p==a))
    return dict(status='human labels supplied' if accepted or agreements else 'pending human labels',sample_size=len(cases),labeled_candidates=len(accepted),predicted_accepts_labeled=len(selected),acceptance_precision=sum(r['human_accept']=='yes' for r in selected)/len(selected) if selected else None,pairwise_n=len(agreements),pairwise_agreement=sum(agreements)/len(agreements) if agreements else None,limits='No recall estimate. Ties excluded from pairwise denominator. Development regressions are not independent human labels.')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--labels');ap.add_argument('--pairs');ap.add_argument('--attest-human',action='store_true');args=ap.parse_args()
    if (args.labels or args.pairs) and not args.attest_human:ap.error('Use --attest-human only for genuine human judgments; never AI-generated labels')
    from run_pipeline import DEFAULT_INPUT
    from src.parser import parse_folder
    from src.llm_evaluator import evaluate_offline
    frozen=json.loads((ROOT/'evaluation/frozen_cases.json').read_text());episodes=parse_folder(DEFAULT_INPUT)
    predictions={c['candidate']['id']:evaluate_offline(c['candidate'].copy(),episodes) for c in frozen['cases']}
    labels=list(csv.DictReader(open(args.labels))) if args.labels else [];pairs=list(csv.DictReader(open(args.pairs))) if args.pairs else []
    result=metrics(frozen['cases'],predictions,labels,pairs);result['selection_method']=frozen['method'];result['frozen_source_sha256']=frozen['source_sha256']
    (ROOT/'evaluation/metrics.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
