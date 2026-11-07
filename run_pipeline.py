#!/usr/bin/env python3
"""Reproducible offline run; environment keys auto-enable a bounded AI shortlist."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from time import perf_counter
from src.editorial_policy import apply_policy,ordering
from src.quality_auditor import validate
from src.parser import parse_folder
from src.inputs import parse_episode_selection
from src.candidate_generator import generate
from src.llm_evaluator import judge,evaluate_offline,DEFAULT_WEIGHTS,validate_weights
from src.quality_auditor import audit,audit_markdown
from src.economics import estimate,cost,RATES

DEFAULT_INPUT=Path(__file__).parent/'I Married a Broken Soldier. He was a Duke'

def execute(episodes,provider='auto',model=None,api_key=None,minimum=20,maximum=60,weights=None,budget=8,episode_numbers=None,on_progress=None):
    def progress(step,message):
        if on_progress: on_progress(step,message)
    if not episodes: raise ValueError('At least one parsed episode is required')
    loaded_episode_count=len(episodes)
    if episode_numbers is not None:
        selected=set(episode_numbers)
        if not selected: raise ValueError('Choose at least one episode')
        missing=selected-{e.number for e in episodes}
        if missing: raise ValueError('Selected episodes are not in this input: '+', '.join(map(str,sorted(missing))))
        episodes=[e for e in episodes if e.number in selected]
    weights=validate_weights(weights or DEFAULT_WEIGHTS)
    start=perf_counter()
    progress(1,'Finding hook and cliffhanger windows…')
    candidates,rejected=generate(episodes,minimum,maximum,max_episode_gap=None if episode_numbers is not None else 3)
    progress(2,f'Scoring {len(candidates)} candidates'+(' and requesting optional AI critique…' if provider!='Heuristic/Offline' and budget else ' offline…'))
    items,usage=judge(episodes,candidates,provider,model,api_key,weights,budget)
    rejected=[evaluate_offline(x,episodes,weights) for x in rejected]
    progress(3,'Applying editorial rules and ranking cuts…')
    eligible=[]
    for item in items:
        apply_policy(item,validate(item,episodes,minimum,maximum))
        if not item['decision']['eligible']:
            rejected.append(dict(item,rejection_reason='; '.join(item['decision']['reasons'])))
        else: eligible.append(item)
    items=sorted(eligible,key=ordering)
    for rank,item in enumerate(items,1): item['rank']=rank
    posting=sorted(items,key=ordering)
    for priority,item in enumerate(posting,1): item['posting_priority']=priority
    progress(4,'Validating timestamps, whole dialogue and overlaps…')
    quality=audit(episodes,items,rejected,minimum,maximum)
    if quality['hard_failures']: raise ValueError(f"Hard audit failed: {quality['hard_failures']}")
    progress(5,'Preparing the ranked playbook…')
    rates=RATES.get(usage['model'])
    usage['actual_cost_at_reference_rates_usd']=cost(usage['input_tokens'],usage['output_tokens'],*rates) if rates else (0 if usage['calls']==0 else None)
    return dict(schema_version='2.0',run=dict(episode_count=len(episodes),loaded_episode_count=loaded_episode_count,
                selected_episode_numbers=sorted(e.number for e in episodes),episode_selection='manual' if episode_numbers is not None else 'all',
                beat_count=sum(len(e.beats) for e in episodes),
                rejected_candidate_count=len(rejected),timeline_slice_count=sum(len(e.timeline) for e in episodes),provider=usage,weights=weights or DEFAULT_WEIGHTS,
                minimum=minimum,maximum=maximum,elapsed_seconds=round(perf_counter()-start,4),
                raw_script_token_estimate=sum(len(b.text) for e in episodes for b in e.beats)//4,
                ranking_policy="Heuristic scores only determine ordering: recommended script candidates before review-required, then heuristic composite. AI assessments can veto or require review; AI scores remain separate, uncalibrated diagnostics.",ai_assessed_shortlisted=sum(bool(x.get("ai_assessment")) for x in items),
                disclaimer='Script-only editorial shortlist. Not validated against footage or ad performance.',
                episode_coverage=[dict(episode=e.number,filename=e.filename,logline=e.logline,candidates=sum(any(s['episode']==e.number for s in x['segments']) for x in items)) for e in episodes]),
                promos=items,rejected_candidates=rejected,audit=quality,economics=estimate())

def write_outputs(result,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    previous=out/'all_episodes_promos_ranked.json'
    if previous.exists():
        import shutil
        snapshot=out/'history'/hashlib.sha256(previous.read_bytes()).hexdigest()[:16]
        if not snapshot.exists():
            snapshot.mkdir(parents=True)
            for p in out.iterdir():
                if p.is_file() and p.suffix in ('.json','.csv','.md'):shutil.copy2(p,snapshot/p.name)
    (out/'all_episodes_promos_ranked.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    fields=['rank','posting_priority','posting_strategy','posting_reason','episodes','segments','duration','hook_text','cliffhanger_text','why_it_works','ranking_rationale','composite_score','evaluation_source',*DEFAULT_WEIGHTS,'editorial_flags','decision','uncertainty','heuristic_scores','ai_scores','score_disagreements']
    with (out/'top_promos_ranked.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for x in result['promos']:
            row={k:x[k] for k in fields if k in x}
            row.update(episodes=','.join(str(s['episode']) for s in x['segments']),segments=format_segments(x),**x['scores'])
            row['editorial_flags']='; '.join(x['editorial_flags'])
            for k in ('decision','uncertainty','heuristic_scores','ai_scores','score_disagreements'):row[k]=json.dumps(x.get(k),ensure_ascii=False)
            # Prevent spreadsheet formula interpretation of screenplay dialogue.
            writer.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for k,v in row.items()})
    lines=['# Promo posting playbook','',f"{result['run']['episode_count']} episodes · {len(result['promos'])} promos · {result['run']['provider']['provider']}",'',result['run']['disclaimer'],'',
           '## Posting strategy','Release reviewed Tier 1 interpersonal hooks first. Test humiliation versus protective rage with equal spend; compare 3-second retention and click-through. Use Tier 2 for audiences familiar with the characters. Review Tier 3 bridges as trailers. Scores predict editorial fit, not measured performance.','',
           '## Recommended posting order','']
    for x in sorted(result['promos'],key=lambda x:x['posting_priority'])[:5]:
        lines.append(f"{x['posting_priority']}. {format_segments(x)} ({x['duration']:.2f}s): {x['posting_reason']} Review: {'; '.join(x['editorial_flags']) or 'No automated flags; footage review still required.'}")
    lines.extend(['','## Episode coverage',''])
    lines += [f"- Episode {e['episode']}: {e['candidates']} candidates" for e in result['run']['episode_coverage']]
    for x in result['promos']:
        lines.extend(['',f"## #{x['rank']} · {x['composite_score']}/100 · {format_segments(x)}",f"**{x['posting_strategy']}** · {x['duration']:.2f}s · Posting priority {x['posting_priority']}",f"Hook: {x['hook_text']}",f"Cut: {x['cliffhanger_text']}",f"Why: {x['why_it_works']}",f"Posting reason: {x['posting_reason']}",f"Rationale: {x['ranking_rationale']}",f"Script decision: {json.dumps(x.get('decision'),ensure_ascii=False)}",f"Uncertainty: {x.get('uncertainty')}",f"Heuristic scores: {x.get('heuristic_scores')}; separate AI scores: {x.get('ai_scores')}",f"Score source: {x['evaluation_source']}",f"Scores: {json.dumps(x['scores'])}",f"Review flags: {'; '.join(x['editorial_flags']) or 'Footage confirmation required'}"])
    (out/'top_promos_report.md').write_text('\n\n'.join(lines)+'\n')
    (out/'quality_and_failure_audit.md').write_text(audit_markdown(result['audit'])+'\n')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.name in ['all_episodes_promos_ranked.json','top_promos_ranked.csv','top_promos_report.md','quality_and_failure_audit.md']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

def format_segments(x):
    return ' + '.join(f"E{s['episode']} {s['start_timestamp']}–{s['end_timestamp']}" for s in x['segments'])

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',default=str(DEFAULT_INPUT));ap.add_argument('--output',default='raw_outputs')
    ap.add_argument('--provider',default='auto',choices=['auto','Heuristic/Offline','Gemini','OpenAI','Anthropic'])
    ap.add_argument('--model');ap.add_argument('--min-duration',type=float,default=20);ap.add_argument('--max-duration',type=float,default=60)
    ap.add_argument('--judge-budget',type=int,default=8)
    ap.add_argument('--episodes',help='Analyze only these episode numbers, for example "2,5,8-10"')
    args=ap.parse_args()
    if args.judge_budget<0: ap.error('judge-budget must be nonnegative')
    episodes=parse_folder(args.input)
    try:
        selected=parse_episode_selection(args.episodes,[e.number for e in episodes]) if args.episodes is not None else None
    except ValueError as exc: ap.error(str(exc))
    result=execute(episodes,args.provider,args.model,minimum=args.min_duration,maximum=args.max_duration,budget=args.judge_budget,episode_numbers=selected)
    write_outputs(result,args.output)
    print(f"Parsed {result['run']['episode_count']} episodes / {result['run']['beat_count']} beats. Ranked {len(result['promos'])} promos; audit {result['audit']['passed']}/{result['audit']['hard_checks']} passed. Outputs: {args.output}")
    for error in result['run']['provider']['errors']: print('Judge warning:',error)

if __name__=='__main__':main()
