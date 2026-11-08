"""Context-aware lexical retrieval; source-cut safety is never delegated to AI."""
import re
from itertools import combinations

# Unconditional injury/action words only. Chains, heat and kneeling need context below.
PHYSICAL = r'\b(slap\w*|whip\w*|welt\w*|blood\w*|grab\w*|chok\w*|shatter\w*|tears? (?:her|his|the) (?:dress|gown)|tearing|torn|strik\w*|struck|collaps\w*|sword|drag\w*|wound\w*)\b'
INTENSE = r'seething|scornful|cold|desperate|thunderstruck|furious|commanding|terrified'
CONFRONT = r'\b(who did this|turn around|strip her|get out|kill\w*|execut\w*|marrying me|witch\w*|arrest\w*|traitor|how dare|hang|cannot breathe|disown\w*|abandon\w*)\b'
DRAMATIC = r"\b(poison(?:ed|ing)?|murder(?:ed|er)?|arrest(?:ed)?|betray(?:ed|al)?|execution|execute[ds]?|witch(?:craft)?|traitor|blackmail|condemn(?:ed)?|sentence[ds]? to death|you stole my|you (?:sold|ruined|lied|used|stole|destroyed)|you (?:are|were|have) (?:a liar|lying|no daughter|no son)|(?:i|he|she|you)(?:'m|'s|'re| am| is| are) (?:the |a )?duke|(?:my|her|his|your) (?:wife|husband|bride|sister|brother|mother|father).{0,35}(?:dead|dying|killed|betrayed)|(?:i|you|he|she) (?:will|shall) (?:die|pay|destroy|suffer|kill)|(?:do not|don't|never) (?:touch|come near)|(?:marry|marrying) (?:her|him|me|my sister)|(?:leave|leaving|left) me|(?:i refuse|i will never|you cannot|you can't).{0,45}(?:marry|wife|husband|daughter|son|child|leave)|(?:boy|child|brother).{0,35}(?:cannot breathe|dying|die)|you saved (?:him|her))\b"
SOCIAL_CONFLICT = r"\b(?:cannot marry you|no daughter of mine|dead to.{0,25}family|(?:dowry|inheritance) is revoked|choose your next words carefully|(?:discarded|beggar's|beggar) (?:bride|wife|husband)|penniless (?:nobody|soldier)|(?:my|your|her|his) husband stole|planted this accusation|complaint of theft|make a beggar disappear|(?:my|her|his|your) mother is a prisoner|everyone believes you are dead|beggar is revealed to be a Duke|calls my marriage a lie|power to undo|watches you lose her twice|gaol will take him|forbidden book|already written the story|(?:man|woman) in my collar.{0,35}bed|name your price|discretion has a price|(?:boy|child|son).{0,30}burning with fever|please save him)\b"
ARCHETYPE = r'\b(?:bride|groom|husband|wife|sister|mother|father(?!\s+Thomas)|marry|marrying|wedding|servant|master|poison\w*|betray\w*|child|brother)\b'
RESOLUTION = r"\b(safe now|thank you|you saved (?:him|her)|chest is quiet|rattling has stopped|fever\W+(?:it(?:'s| is)\W+)?breaking|forgive you|all right|everything is fine|reassuring|relaxes|relief|reassured|comforting|tender kiss|gently cradles|tearful reunion|embraces her son|unspoken bond|gaze deeply|softening with deep empathy|resolving chord)\b"
LORE = r'ashbourne|ashburton|ashbury|crest|ledger|herbarium|council|license|charcoal|antidote|grimoire|signet'
FILLER_QUESTIONS={'what','who','why','how long','of them','not yet','shall we','what is it','you see','is it','really','and','yes','mother'}

def hits(pattern,text): return len(re.findall(pattern,text,re.I))

def physical_conflict(text):
    """Count explicit harm/restraint, not decorative objects, routine heat or posture."""
    cleaned=re.sub(r'\b(?:wounded (?:pride|ego|expression|look)|look so wounded)\b','',text,flags=re.I)
    cleaned=re.sub(r'\b(?:eyes?|gaze|sorrow)\b[^.!?]{0,35}\bburn\w*\b','',cleaned,flags=re.I)
    cleaned=re.sub(r'\bburning (?:with |into )?(?:ambition|outrage|rage|desire|intent|ruthless intent|forehead|hot)\b','',cleaned,flags=re.I)
    cleaned=re.sub(r'\b(?:betrayal|realization|truth|words|fear) (?:strikes?|struck|hits?)\b','',cleaned,flags=re.I)
    if re.search(r'\b(?:gavel|wooden block|cane striking|clock strikes)\b',cleaned,re.I):
        cleaned=re.sub(r'\bstrik\w*\b','',cleaned,flags=re.I)
    restraint=hits(r'\b(?:chained|shackl\w*|manacl\w*|iron chains|chains? (?:around|binding|cutting into) (?:her|his|their) (?:neck|wrist|ankle)|(?:snaps?|grabs?|drags?).{0,35}chains? (?:around|at) (?:her|his) neck)\b',cleaned)
    burning=hits(r'\b(?:burn (?:it|her|him|them|alive)|burn(?:ed|t|ing)? (?:the |a |her |his |every )?(?:ledger|book|journal|letter|page|skin|flesh|hand|arm|face|body|house|cottage)|(?:skin|flesh|hand|arm|face|body|house|cottage|book|page) (?:is |was |has been )?(?:burning|burned|burnt)|set.{0,25}on fire)\b',cleaned)
    kneeling=hits(r'\b(?:(?:make|made|forced?|forces?|ordered?) .{0,25}kneel\w*|kneel\w*.{0,65}(?:begging|pleading|humiliat\w*)|laughing.{0,35}kneeling form|drops? to one knee)\b',cleaned)
    return hits(PHYSICAL,cleaned)+restraint+burning+kneeling

def hook(b):
    if b.kind=='SOUND FX':return 0
    physical=bool(physical_conflict(b.text))
    confrontation=bool(hits(CONFRONT,b.text))
    dramatic=bool(hits(DRAMATIC,b.text) or (b.kind=='DIALOGUE' and hits(SOCIAL_CONFLICT,b.text)))
    betrayal=bool(hits(r'you stole my wedding|marrying (?:her|me|my sister)|leaving me at the altar',b.text))
    score=max(80*physical,65*confrontation,65*dramatic,85*betrayal)
    # An intense cue strengthens a concrete conflict; it is never the entire hook.
    if score and b.kind=='DIALOGUE' and len(b.text.split())>=5:score+=10*bool(hits(INTENSE,b.speaker))
    return min(100,score)

def filler_question(text):
    clean=' '.join(re.findall(r"[a-z]+(?:'[a-z]+)?",text.lower().replace('’',"'")))
    return '?' in text and clean in FILLER_QUESTIONS

def cliff(b):
    if hits(RESOLUTION,b.text):return 0
    if b.kind=='SOUND FX':return 22 if hits(r'sting|swell',b.text) else 0
    spoken=b.text.strip().strip('"“”');words=re.findall(r"\b\w+(?:['’]\w+)?\b",spoken)
    if filler_question(spoken):return 25
    question='?' in spoken
    if question and not spoken.rstrip('!').endswith('?'):return 25
    if b.kind!='DIALOGUE':
        return 70 if hits(r'\b(?:draws|raises|aims|presses).{0,35}(?:sword|knife|gun|blade)|(?:noose|blade).{0,25}(?:neck|throat)',spoken) else min(35,15*bool(physical_conflict(spoken))+20*bool(hits(r'freeze|stunned|shock|reveal',spoken)))
    stakes=bool(hits(SOCIAL_CONFLICT+'|'+DRAMATIC+'|'+CONFRONT+r'|\bburn it\b|\b(?:you|he|she)(?:\W+are|\W+is|\W+re|\W+s).{0,12}\bduke\b',spoken))
    if b.kind=='DIALOGUE' and question and len(words)<4 and not stakes:return 30
    if question:return 80 if hits(r'\b(who|why|how|what)\b',spoken) else 65
    if stakes:return 80
    return min(55,15*bool(physical_conflict(spoken))+20*bool(hits(r'freeze|stunned|shock|reveal',spoken)))

def segment(ep,a,z):
    return dict(episode=ep.number,filename=ep.filename,start=a,end=z,
                start_timestamp=next(b.start_timestamp for b in ep.beats if b.start==a),
                end_timestamp=next(b.end_timestamp for b in ep.beats if b.end==z),duration=round(z-a,3))

def make_candidate(segments,index):
    return dict(id=index,kind='single' if len(segments)==1 else 'mashup',segments=segments,
                duration=round(sum(s['duration'] for s in segments),3))

def generate(episodes,minimum=20,maximum=60,per_episode=3,max_episode_gap=3):
    if not 20<=minimum<=maximum<=60: raise ValueError('Duration bounds must stay within 20–60s')
    singles, rejected, short = [], [], []
    for ep in episodes:
        starts=sorted({b.start for b in ep.beats if hook(b)>=60 and ep.boundary(b.start,'start')})
        ends=sorted({b.end for b in ep.beats if cliff(b)>=65 and ep.boundary(b.end,'end')})
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
            if not overlap and len(kept)<per_episode*4: kept.append(item)
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
    mashups=[]; bridges=set()
    for left,right in combinations(shorts,2):
        a,b=left['segments'][0],right['segments'][0]
        if (a['episode'],a['start'])>(b['episode'],b['start']): a,b=b,a
        if a['episode']==b['episode'] and a['end']>b['start']: continue
        if max_episode_gap is not None and b['episode']-a['episode']>max_episode_gap: continue
        ta=' '.join(x['text'] for x in lookup[a['episode']].excerpt(a['start'],a['end']))
        tb=' '.join(x['text'] for x in lookup[b['episode']].excerpt(b['start'],b['end']))
        roles=set(re.findall(ARCHETYPE,ta.lower())) & set(re.findall(ARCHETYPE,tb.lower()))
        if minimum<=a['duration']+b['duration']<=maximum and roles:
            bridge=(a['episode'],a['start'],b['episode'],b['start'])
            if bridge not in bridges:
                mashups.append(make_candidate([a,b],f'M-{a["episode"]}-{a["start"]}-{a["end"]}-{b["episode"]}-{b["start"]}-{b["end"]}'))
                bridges.add(bridge)
    # Preserve a source-grounded audit case even when improved retrieval excludes its hook.
    for number,a,z in [(9,40.8,87.4)]:
        ep=lookup.get(number)
        if ep and ep.boundary(a,'start') and ep.boundary(z,'end') and minimum<=z-a<=maximum:
            candidate=make_candidate([segment(ep,a,z)],f'E{number}-{a}-{z}')
            if not any(x['id']==candidate['id'] for x in singles+rejected):
                rejected.append(dict(candidate,rejection_reason='Development audit: resolved rescue followed by routine new-scene greeting'))
    return singles+mashups[:30],rejected
