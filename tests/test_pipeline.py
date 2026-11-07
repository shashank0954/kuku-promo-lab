from copy import deepcopy
import json
from unittest.mock import patch
import pytest
from src.parser import parse_folder,parse_text,seconds
from src.candidate_generator import generate,hook,cliff
from src.llm_evaluator import evaluate_offline,judge,DIMENSIONS,JudgeProvider
from src.quality_auditor import validate
from run_pipeline import DEFAULT_INPUT,execute

@pytest.fixture(scope='module')
def episodes():
    if not DEFAULT_INPUT.exists():
        pytest.skip('Confidential source pack is not bundled; restore it to run source integration tests')
    return parse_folder(DEFAULT_INPUT)

def test_parse_all_lossless_overlap(episodes):
    assert len(episodes)==50
    assert sum(len(e.beats) for e in episodes)==3727
    assert any(len(s['beat_ids'])>=3 for e in episodes for s in e.timeline)
    for e in episodes:
        for b in e.beats:
            coverage=sum(s['end']-s['start'] for s in e.timeline if b.id in s['beat_ids'])
            assert coverage==pytest.approx(b.end-b.start)
        assert all(a['end']==b['start'] for a,b in zip(e.timeline,e.timeline[1:]))
    assert episodes[21].warnings
    assert seconds('(02:18.00)')==138

def test_safety_and_timestamp_tampering(episodes):
    items,_=generate(episodes)
    assert items and any(x['kind']=='mashup' for x in items)
    assert len({x['id'] for x in items})==len(items)
    for item in items: assert not validate(item,episodes)
    x=deepcopy(items[0]);x['segments'][0]['start_timestamp']='99:99.99'
    assert 'Non-verbatim start boundary' in validate(x,episodes)
    b=next(b for b in episodes[0].beats if b.kind=='DIALOGUE')
    assert not episodes[0].safe((b.start+b.end)/2)
    x=deepcopy(items[0]);x['duration']+=1
    assert 'Total duration mismatch' in validate(x,episodes)

def test_regression_music_and_tears(episodes):
    b=deepcopy(episodes[0].beats[0]);b.kind='SOUND FX';b.text='A cliffhanger swell.'
    assert hook(b)==0 and cliff(b)<=22
    b.kind='CAMERA';b.text='Her tear-streaked face.'
    assert hook(b)==0
    b.kind='DIALOGUE';b.text='Are you hurt? No. I am fine.'
    assert cliff(b)<35

def test_offline_reproducibility(episodes):
    a=execute(episodes,'Heuristic/Offline');b=execute(episodes,'Heuristic/Offline')
    assert a['promos']==b['promos']
    assert not a['audit']['hard_failures']
    assert a['run']['provider']['input_tokens']==0
    assert len(a['run']['episode_coverage'])==50

def test_provider_schema_and_error_fallback(episodes):
    items,_=generate(episodes)
    with patch.object(JudgeProvider,'request',return_value=({'results':[]},{'input_tokens':10,'output_tokens':1})):
        ranked,stats=judge(episodes,items[:4],'Gemini','gemini-2.5-flash','fake-key',budget=4)
    assert stats['errors'] and stats['judged_candidates']==0
    assert all(x['evaluation_source']=='heuristic' for x in ranked)
    def valid_request(self,prompt):
        evidence=json.loads(prompt.split('Evidence: ',1)[1])
        return {'results':[{'id':x['id'],'scores':{k:77 for k in DIMENSIONS},'rationale':'Test critique','why':'Test evidence','flags':[]} for x in evidence]}, {'input_tokens':100,'output_tokens':20}
    with patch.object(JudgeProvider,'request',valid_request):
        ranked,stats=judge(episodes,items[:4],'OpenAI','gpt-4o-mini','fake-key',budget=4)
    assert stats['judged_candidates']==4 and stats['input_tokens']==100
    assert all(x['composite_score']==77 for x in ranked)
    assert all(not validate(x,episodes) for x in ranked)

def test_invalid_input():
    with pytest.raises(ValueError):parse_text('not a screenplay')
    with pytest.raises(ValueError):generate([],10,60)

@pytest.mark.parametrize('provider',['Gemini','OpenAI','Anthropic'])
def test_rest_adapters(provider):
    if provider=='Gemini':
        response={'candidates':[{'content':{'parts':[{'text':'{"results": []}'}]}}],'usageMetadata':{'promptTokenCount':10,'candidatesTokenCount':2,'thoughtsTokenCount':3}}
    elif provider=='OpenAI':
        response={'choices':[{'message':{'content':'{"results": []}'}}],'usage':{'prompt_tokens':10,'completion_tokens':5}}
    else:
        response={'content':[{'text':'{"results": []}'}],'usage':{'input_tokens':10,'output_tokens':5}}
    class Reply:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return json.dumps(response).encode()
    with patch('urllib.request.urlopen',return_value=Reply()) as call:
        data,usage=JudgeProvider(provider,'test-model','secret').request('prompt')
    assert data=={'results':[]} and usage=={'input_tokens':10,'output_tokens':5}
    assert call.call_args[0][0].full_url.startswith('https://')
