"""Independent cut validator plus editorial diagnostics (not a semantic proof)."""
from .candidate_generator import hits, RESOLUTION

def validate(item,episodes,minimum=20,maximum=60):
    lookup={e.number:e for e in episodes}; errors=[]; total=0
    segs=item.get('segments',[])
    if not 1<=len(segs)<=3: errors.append('Segment count must be 1–3')
    for s in segs:
        ep=lookup.get(s['episode'])
        if not ep: errors.append('Unknown episode'); continue
        if s.get('filename')!=ep.filename: errors.append('Filename does not match source episode')
        if s['end']<=s['start']: errors.append('Nonpositive segment duration')
        total+=s['end']-s['start']
        if abs(s['duration']-(s['end']-s['start']))>1e-6: errors.append('Segment duration mismatch')
        for side in ('start','end'):
            value=s[side]; stamp=s[f'{side}_timestamp']
            if not any(getattr(b,side)==value and getattr(b,f'{side}_timestamp')==stamp for b in ep.beats): errors.append(f'Non-verbatim {side} boundary')
            if not ep.safe(value): errors.append(f'Mid-dialogue {side} cut')
    if not minimum-1e-6<=total<=maximum+1e-6: errors.append('Duration outside configured 20–60s bounds')
    if abs(total-item.get('duration',-1))>1e-6: errors.append('Total duration mismatch')
    for i,a in enumerate(segs):
        for b in segs[i+1:]:
            if a['episode']==b['episode'] and max(a['start'],b['start'])<min(a['end'],b['end']): errors.append('Overlapping reused footage')
    return errors

def audit(episodes,items,rejected,minimum=20,maximum=60):
    checks=[dict(id=x['id'],errors=validate(x,episodes,minimum,maximum)) for x in items+rejected]
    failures=[c for c in checks if c['errors']]
    examples=[]
    for x in items+rejected:
        flags=x.get('editorial_flags',[])
        if flags:
            reason=x.get('rejection_reason','')
            fix=('Move the in-point to a physical action or shocking line, then revalidate duration.' if any('Weak first' in f for f in flags) else
                 'Cut before the recovery; reject the clip if the remaining unresolved stretch is too short.' if any('Main conflict resolves' in f or 'De-escalation' in f for f in flags) else
                 'Preserve a single victim and causal conflict; remove the misleading bridge.' if any('changes apparent victim' in f for f in flags) else
                 'Choose a cut with explicit human relationships and threats instead of unexplained lore.' if any('Backstory' in f for f in flags) else
                 'Check exact first-three-second action/word timing in footage and reject if the hook starts late.' if any('onset' in f or 'exceeds 3s' in f for f in flags) else
                 'Watch the exact cut in footage; verify unresolved stakes and identity continuity.')
            examples.append(dict(id=x['id'],segments=x['segments'],score=x.get('composite_score'),
                                 hook=x.get('hook_text',''),cut=x.get('cliffhanger_text',''),
                                 categories=flags,status='shortlisted but flagged' if x in items else 'rejected candidate',
                                 rejection_reason=reason,human_fix=fix))
    # Retain diverse concrete failures, not 20 near-duplicates.
    diverse=[]; counts={}
    for x in sorted(examples,key=lambda x:(x['status']!='rejected candidate',x['score'] or 0)):
        category=x['categories'][0]
        if counts.get(category,0)<5:
            diverse.append(x); counts[category]=counts.get(category,0)+1
    represented=set()
    for x in examples:
        if any(c not in represented for c in x['categories']):
            represented.update(x['categories'])
            if x not in diverse: diverse.insert(0,x)
    return dict(ranked_checks=len(items),rejected_checks=len(rejected),hard_checks=len(checks),hard_failures=failures,passed=len(checks)-len(failures),
                source_warnings=[w for e in episodes for w in e.warnings],
                editorial_flagged=sum(bool(x.get('editorial_flags')) for x in items),
                failure_examples=diverse,method='Structural cut checks pass when reported; hook, clarity, and unresolved tension remain heuristic/editorial judgments.')

def audit_markdown(result):
    out=['# Quality & honest failure audit','',f"Validated {result['hard_checks']} candidates ({result['ranked_checks']} shortlisted / {result['rejected_checks']} rejected); {result['passed']} passed hard constraints; {len(result['hard_failures'])} failed.",
         '',result['method'],'',f"Editorial review flags: {result['editorial_flagged']}.",'','## Source anomalies',*['- '+w for w in result['source_warnings']],'','## Actual weak picks and rejected opening baselines','']
    for x in result['failure_examples']:
        cuts=' + '.join(f"E{s['episode']} {s['start_timestamp']}–{s['end_timestamp']}" for s in x['segments'])
        out.extend([f"### {x['id']} · {cuts} · {x['status']}",f"Score: {x['score']}. Categories: {'; '.join(x['categories'])}.",f"Opening evidence: {x['hook']}",f"Cut evidence: {x['cut']}",f"Human correction: {x['human_fix']}",''])
    out.extend(['## Release gate','Editors must verify action onset, unanswered stakes, audio continuity, and mashup identity in footage before posting. No CTR, view-through or conversion lift has been measured.','Hard failures are never exported as valid promos. This file is generated directly from run diagnostics.'])
    return '\n\n'.join(out)
