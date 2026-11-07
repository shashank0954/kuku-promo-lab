"""Recall-first lexicon retrieval; endpoint safety is never delegated to AI."""
import re
from itertools import combinations

PHYSICAL = r'\b(slap\w*|whip\w*|welt\w*|blood\w*|kneel\w*|grab\w*|chok\w*|shatter\w*|tears? (?:her|his|the) (?:dress|gown)|tearing|torn|strik\w*|struck|collaps\w*|sword|burn\w*|chain\w*|drag\w*|wound\w*)\b'
INTENSE = r'seething|scornful|cold|desperate|thunderstruck|furious|commanding|terrified'
CONFRONT = r'\b(who did this|turn around|strip her|get out|kill\w*|execut\w*|marrying me|witch\w*|arrest\w*|traitor|how dare|hang|cannot breathe|disown\w*|abandon\w*)\b'
ARCHETYPE = r'bride|groom|husband|wife|sister|mother|father|marry|marrying|wedding|servant|master|poison|betray|child|brother'
RESOLUTION = r'\b(safe now|thank you|forgive you|all right|everything is fine|reassuring|relaxes|relief|reassured|comforting|tender kiss|gently cradles|tearful reunion|embraces her son|unspoken bond|gaze deeply|softening with deep empathy|resolving chord)\b'
LORE = r'ashbourne|ashburton|ashbury|crest|ledger|herbarium|council|license|charcoal|antidote|grimoire|signet'

def hits(pattern,text): return len(re.findall(pattern,text,re.I))
def hook(b):
    if b.kind=='SOUND FX': return 0
    physical=bool(hits(PHYSICAL,b.text))
    confrontation=bool(hits(CONFRONT,b.text))
    # Parenthetical heat alone is recall evidence, not a shocking opening line.
    score=80*physical+65*confrontation
    if b.kind=='DIALOGUE' and len(b.text.split())>=5:
        score+=18*bool(hits(INTENSE,b.speaker))
    elif hits(INTENSE,b.speaker): score+=8
    return min(100,score)
def cliff(b):
    if hits(RESOLUTION,b.text): return 0
    if b.kind=='SOUND FX': return 22 if hits(r'sting|swell',b.text) else 0
    spoken=b.text.strip().strip('"“”')
    question='?' in spoken
    answered_in_line=question and not spoken.endswith('?')
    if answered_in_line: return 25
    threat=bool(hits(r'\b(arrest\w*|execut\w*|hang|strip her|kill you|traitor|witch|will (?:die|pay|burn|suffer)|shall (?:die|pay|burn|suffer))\b',spoken))
    urgent=bool(hits(r'who|why|how|what',spoken))
    return min(100, 65*question + 15*(question and urgent) + 70*threat +
               15*bool(hits(PHYSICAL,b.text)) + 20*bool(hits(r'freeze|stunned|shock|reveal',b.text)))

def segment(ep,a,z):
    return dict(episode=ep.number,filename=ep.filename,start=a,end=z,
                start_timestamp=next(b.start_timestamp for b in ep.beats if b.start==a),
                end_timestamp=next(b.end_timestamp for b in ep.beats if b.end==z),duration=round(z-a,3))

def make_candidate(segments,index):
    return dict(id=index,kind='single' if len(segments)==1 else 'mashup',segments=segments,
                duration=round(sum(s['duration'] for s in segments),3))

def generate(episodes,minimum=20,maximum=60,per_episode=8):
    if not 20<=minimum<=maximum<=60: raise ValueError('Duration bounds must stay within 20–60s')
    singles, rejected, short = [], [], []
    for ep in episodes:
        starts=sorted({b.start for b in ep.beats if hook(b)>=28 and ep.boundary(b.start,'start')})
        ends=sorted({b.end for b in ep.beats if cliff(b)>=22 and ep.boundary(b.end,'end')})
        pool=[]
        for a in starts:
            for z in ends:
                d=round(z-a,3)
                if 6<=d<=maximum and ep.safe(z):
                    item=make_candidate([segment(ep,a,z)],f'E{ep.number}-{a}-{z}')
                    first=[b for b in ep.beats if a<=b.start<a+3]
                    last=[b for b in ep.beats if z-4<b.end<=z]
                    score=max([hook(b) for b in first] or [0])+max([cliff(b) for b in last] or [0])
                    item['retrieval_score']=score
                    if minimum<=d<=maximum: pool.append(item)
                    elif d<=24: short.append(item)
        # Temporal diversity: reject heavily overlapping alternatives, preserving audit trail.
        kept=[]
        for item in sorted(pool,key=lambda x:(-x['retrieval_score'],x['duration'],x['id'])):
            s=item['segments'][0]
            overlap=any(max(0,min(s['end'],k['segments'][0]['end'])-max(s['start'],k['segments'][0]['start'])) / min(item['duration'],k['duration'])>.65 for k in kept)
            if not overlap and len(kept)<per_episode: kept.append(item)
            elif len(rejected)<200: rejected.append(dict(item,rejection_reason='Redundant overlap or lower retrieval rank'))
        singles.extend(kept)
        # Deliberately audit the real opening, even if atmospheric or resolving.
        end=next((z for z in sorted({b.end for b in ep.beats}) if z>=minimum and ep.boundary(z,'end')),None)
        if end and end<=maximum and ep.boundary(0,'start'):
            rejected.append(dict(make_candidate([segment(ep,0,end)],f'OPEN-{ep.number}'),rejection_reason='Opening baseline: test first-three-second false positives'))
    # Match on shared interpersonal roles, restrict chronology and retain only a small trailer pool.
    lookup={e.number:e for e in episodes}
    short=sorted(short,key=lambda x:(-x['retrieval_score'],x['id']))
    shorts=[]
    for item in short:
        if sum(x['segments'][0]['episode']==item['segments'][0]['episode'] for x in shorts)<2: shorts.append(item)
    mashups=[]
    for left,right in combinations(shorts,2):
        a,b=left['segments'][0],right['segments'][0]
        if (a['episode'],a['start'])>(b['episode'],b['start']): a,b=b,a
        if a['episode']==b['episode'] and a['end']>b['start']: continue
        if b['episode']-a['episode']>3: continue
        ta=' '.join(x['text'] for x in lookup[a['episode']].excerpt(a['start'],a['end']))
        tb=' '.join(x['text'] for x in lookup[b['episode']].excerpt(b['start'],b['end']))
        roles=set(re.findall(ARCHETYPE,ta.lower())) & set(re.findall(ARCHETYPE,tb.lower()))
        if minimum<=a['duration']+b['duration']<=maximum and roles:
            mashups.append(make_candidate([a,b],f'M-{a["episode"]}-{a["start"]}-{a["end"]}-{b["episode"]}-{b["start"]}-{b["end"]}'))
    return singles+mashups[:30],rejected
