"""Shared editorial policy. Structural validity is independent of script judgment."""
ASSESSMENTS=('opening','conflict','unresolved','already_answered','missing_context','continuity')
BLOCKING={'resolved','subplot_pivot','music_only','victim_change','missing_object'}

def decide(item,hard_failures=()):
    scores=item.get('heuristic_scores',item['scores'])
    concerns=item.get('heuristic_concerns',[])
    reasons=[c['reason'] for c in concerns if c['code'] in BLOCKING]
    for key in ('hook_3s_score','cliffhanger_score','standalone_clarity_score'):
        if scores[key]<55: reasons.append(f'{key} below retrieval threshold (55)')
    ai=item.get('ai_assessment')
    if ai and ai['already_answered']['verdict']=='yes':reasons.append('AI finds the selected clip already answers the ending question')
    if ai and any(ai[k]['verdict']=='concern' for k in ('opening','conflict','unresolved')):reasons.append('AI identifies an editorial concern in hook, conflict or ending')
    uncertainty=item.get('uncertainty',[])
    if ai and ai['continuity']['verdict']=='concern' and 'requires continuity review' not in uncertainty:uncertainty=uncertainty+['requires continuity review']
    status='rejected' if hard_failures or reasons else 'review_required' if any(x!='supported by script timing' for x in uncertainty) else 'recommended'
    needs=[x for x in uncertainty if x!='supported by script timing']
    return dict(status=status,eligible=status!='rejected',hard_failures=list(hard_failures),heuristic_concerns=concerns,ai_findings=ai or {},reasons=list(hard_failures)+reasons+needs or ['Script supports opening and unresolved endpoint; footage review remains required'],footage_approved=False)

def apply_policy(item,hard_failures=()):
    item['decision']=decide(item,hard_failures)
    item['editorial_status']=item['decision']['status']+' — script assessment only'
    return item

def ordering(item):
    # One comparable heuristic ordering; AI is a separate critique/veto, never substituted.
    return (item.get('decision',{}).get('status')!='recommended',-item.get('heuristic_composite_score',item['composite_score']),item['id'])

def judging_sample(items,budget):
    ordered=sorted(items,key=lambda x:(-x['composite_score'],x['id']))
    if budget<=0:return []
    borderline=sorted(items,key=lambda x:(min(abs(x['scores'][k]-55) for k in ('hook_3s_score','cliffhanger_score','standalone_clarity_score')),x['id']))
    top_count=max(1,budget-(budget//3))
    selected=ordered[:top_count]
    for x in borderline+ordered:
        if len(selected)>=budget:break
        if x not in selected:selected.append(x)
    return selected

def validate_assessment(value,item,episodes):
    if not isinstance(value,dict) or set(value)!=set(ASSESSMENTS):raise ValueError('Missing structured editorial assessments')
    lookup={e.number:e for e in episodes}
    allowed={b.id:b for s in item['segments'] for b in lookup[s['episode']].beats if b.start<s['end'] and b.end>s['start']}
    first=item['segments'][0];last=item['segments'][-1]
    for key,a in value.items():
        if not isinstance(a,dict) or set(a)!={'text','evidence','verdict'} or not isinstance(a['text'],str) or not a['text'].strip() or a['verdict'] not in ('supported','concern','insufficient','yes','no'):raise ValueError('Invalid assessment')
        if key=='already_answered' and a['verdict'] not in ('yes','no','insufficient'):raise ValueError('Answer assessment requires yes/no/insufficient')
        if key!='already_answered' and a['verdict'] not in ('supported','concern','insufficient'):raise ValueError('Invalid editorial verdict')
        refs=a['evidence']
        if not isinstance(refs,list) or not refs or any(not isinstance(r,str) or r not in allowed for r in refs):raise ValueError('Unsupported AI evidence reference')
        if key=='opening' and any(not (r.startswith(str(first['episode'])+':') and allowed[r].start<first['start']+3 and allowed[r].end>first['start']) for r in refs):raise ValueError('Opening evidence outside first three seconds')
        if key=='unresolved' and any(not (r.startswith(str(last['episode'])+':') and allowed[r].end>last['end']-4 and allowed[r].start<last['end']) for r in refs):raise ValueError('Ending evidence outside cut window')
    return value
