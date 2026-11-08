"""Source-specific editorial explanations; role labels alone never define a theme."""
import re
from .candidate_generator import hits,physical_conflict,filler_question

def content_text(beats):
    # Speaker cues stay available for delivery scoring, never appended to theme text.
    text=' '.join(b.text for b in beats if b.kind!='SOUND FX')
    return re.sub(r'\b(?:the former groom|lady in (?:a )?gold gown|blond nobleman|aristocratic woman)\b','the character',text,flags=re.I)

def classify_theme(text):
    if hits(r'\b(witch|witchcraft|execut\w*|stake|heretic)\b',text):return 'Witchcraft Framing & Execution Threat'
    if hits(r"\b(?:you(?:'re| are)|he(?:'s| is)|i(?:'m| am)) (?:really |actually |the )*duke\b|beggar.{0,35}revealed to be a duke|duke.{0,20}(?:identity|secret)",text):return 'Hidden Identity / Duke Reveal'
    if hits(r'\b(child|boy|brother|patient|fever|medicine|breathe|dying)\b',text) and hits(r'\b(sick|fever|burning|ill|die|dying|breathe|saved|medicine|doctor)\b',text):return 'Life-or-Death Medical Crisis'
    if physical_conflict(text) or hits(r'\b(?:poisoned my|tortured my)\b',text):return 'Physical Peril & Protective Rage'
    if hits(r'\b(wedding|altar|marrying|bride|fianc[eé])\b',text):return 'Altar Betrayal & Humiliation'
    if hits(r'\b(council|estate|manor|ledger|poison|conspir\w*|inherit\w*|registry|arrest\w*)\b',text):return 'Aristocratic Conspiracy'
    if hits(r'\b(wife|husband|marry|love|losing you|leave me)\b',text):return 'Romantic Betrayal & Emotional Ultimatum'
    return 'Interpersonal Accusation & Power Struggle'

def one_liner(theme,h,c,scores,concerns):
    def short(text,n):
        value=' '.join(text.strip('"“”').split());return value if len(value)<=n else value[:n-1]+'…'
    if h.kind=='DIALOGUE':
        impact=('makes the stolen wedding and humiliation instantly clear' if hits(r'you stole my wedding|marrying (?:me|my sister)',h.text) else
                'makes a child’s survival an immediate decision' if hits(r'brother|child|cannot breathe|only hope',h.text) else
                'makes public abuse a personal accusation' if hits(r'church chained me',h.text) else
                'puts coercion and the risk of refusal in the first line' if hits(r'burn|witch|execut|die|arrest',h.text) else
                'turns rejection or accusation into an immediate personal conflict')
    else:
        impact=('puts a physical attack on screen immediately' if hits(r'strike|struck|slap|whip|drags|chok',h.text) else
                'makes an injury or restraint visible before the explanation' if hits(r'wound|welt|blood|chain|shackle',h.text) else
                'opens on a visible kneeling pledge before the conflict escalates' if hits(r'drops to one knee',h.text) else
                'puts a concrete action ahead of exposition')
    opening=f'“{short(h.text,85)}” {impact}'
    if scores['hook_3s_score']<55:opening=f'“{short(h.text,85)}” offers no substantiated first-three-second confrontation'
    if any(x['code']=='resolved_mid_clip' for x in concerns):ending='the rescue resolves before a new conversation, so its apparent cliffhanger is a false handoff'
    elif filler_question(c.text):ending=f'“{short(c.text,65)}” is filler, so this ending should be rejected'
    else:
        gap=('leaves the abandoned bride’s future undecided' if hits(r'what happens to me',c.text) else
             'leaves the attacker’s identity unanswered' if hits(r'who did this',c.text) else
             'leaves the threat to undo the marriage hanging' if hits(r'power to undo|lose her twice',c.text) else
             'leaves an execution or punishment unresolved' if hits(r'execut|witch|hang|die',c.text) else
             'demands a motive without supplying the reply' if '?' in c.text and hits(r'\bwhy\b',c.text) else
             'leaves the challenge to identity or authority unanswered' if '?' in c.text and hits(r'\bwho\b',c.text) else
             'leaves the decision demanded by the question open' if '?' in c.text else
             'leaves the poisoning accusation and its consequences unsettled' if hits(r'poison',c.text) else
             'leaves two incompatible accounts in direct conflict' if hits(r'lying|liar',c.text) else
             'cuts before the threat or accusation receives a response')
        ending=f'“{short(c.text,85)}” {gap}'
    return f'{theme}: {opening}; {ending}.'
