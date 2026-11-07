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
    assert any(e.dialogue_joins for e in episodes)
    for e in episodes:
        for a,z in e.dialogue_joins:
            assert not e.safe(a) and not e.safe(z)

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

def test_regression_music_and_tears():
    b=deepcopy(parse_folder('examples')[0].beats[0]);b.kind='SOUND FX';b.text='A cliffhanger swell.'
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
        model='gemini-3.8-flash' if provider=='Gemini' else 'test-model'
        data,usage=JudgeProvider(provider,model,'secret').request('prompt')
    assert data=={'results':[]} and usage=={'input_tokens':10,'output_tokens':5}
    assert call.call_args[0][0].full_url.startswith('https://')
    if provider=='Gemini':
        request=call.call_args[0][0]
        assert 'gemini-3.8-flash:generateContent' in request.full_url
        config=json.loads(request.data)['generationConfig']
        assert config['thinkingConfig']=={'thinkingLevel':'low'}
        assert config['maxOutputTokens']==4096

@pytest.mark.parametrize('text',[
    'A gold pocket watch chain hangs from his immaculate coat.',
    'Her eyes burning with ambition.',
    'She watches with wounded pride.',
    'The judge strikes the wooden block with his gavel.'
])
def test_false_positive_physical_hook(text):
    from src.candidate_generator import physical_conflict
    assert physical_conflict(text)==0
    b=deepcopy(parse_folder('examples')[0].beats[0]);b.kind='CAMERA';b.speaker='CAMERA';b.text=text
    assert hook(b)==0

@pytest.mark.parametrize('number,start,end,expected',[
    (30,3.0,43.5,False),
    (49,84.0,112.8,False),
    (47,14.8,59.8,False),
    (21,47.3,99.2,False),
    (24,0.0,20.5,False),
    (9,13.8,54.0,False),
    (32,3.0,24.8,True),
    (25,13.2,33.8,True),
    (3,8.8,40.4,True),
    (21,11.2,35.8,True),
    (3,84.0,112.5,True),
])
def test_reviewed_editorial_regressions(episodes,number,start,end,expected):
    from src.candidate_generator import segment,make_candidate
    ep=next(e for e in episodes if e.number==number)
    item=evaluate_offline(make_candidate([segment(ep,start,end)],'review-case'),episodes)
    scores=item['scores']
    eligible=(scores['hook_3s_score']>=55 and scores['cliffhanger_score']>=55 and scores['standalone_clarity_score']>=55
              and not any('De-escalation' in f or 'Main conflict resolves' in f or 'Music sting alone' in f for f in item['editorial_flags']))
    assert eligible==expected
    assert not validate(item,episodes)


def test_malformed_ai_json_keeps_billed_usage():
    from src.llm_evaluator import InvalidJudgeResponse
    response={'candidates':[{'content':{'parts':[{'text':'not JSON'}]}}],
              'usageMetadata':{'promptTokenCount':23,'candidatesTokenCount':7}}
    class Reply:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return json.dumps(response).encode()
    with patch('urllib.request.urlopen',return_value=Reply()):
        with pytest.raises(InvalidJudgeResponse) as err:
            JudgeProvider('Gemini','gemini-3.8-flash','fake-key').request('prompt')
    assert err.value.usage=={'input_tokens':23,'output_tokens':7}


def test_question_cannot_outscore_its_later_answer():
    from src.parser import Beat
    from src.candidate_generator import segment,make_candidate
    e=parse_folder('examples')[0]
    original=next(b for b in e.beats if b.kind=='DIALOGUE' and b.start==27)
    e.beats.remove(original)
    e.beats += [Beat('test-q','DIALOGUE','GROOM',27,29,'00:27.00','00:29.00','"Did you steal it?"','01'),
                Beat('test-a','DIALOGUE','BRIDE',29,30.5,'00:29.00','00:30.50','"Yes."','01')]
    e.beats.sort(key=lambda b:b.start)
    item=evaluate_offline(make_candidate([segment(e,7,30.5)],'answered-question'),[e])
    assert item['scores']['cliffhanger_score']<55
    assert item['cliffhanger_evidence']['beat_id']=='test-a'


def gemini_ok_response():
    payload={'candidates':[{'content':{'parts':[{'text':'{"status":"ok"}'}]}}],
             'usageMetadata':{'promptTokenCount':10,'candidatesTokenCount':4}}
    class Reply:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return json.dumps(payload).encode()
    return Reply()


def test_transient_503_recovers_with_bounded_backoff():
    from urllib.error import HTTPError
    messages=[];adapter=JudgeProvider('Gemini','gemini-3.8-flash','fake-key',on_retry=messages.append)
    failures=[HTTPError('https://example.test',503,'unavailable',{},None) for _ in range(2)]
    with patch('urllib.request.urlopen',side_effect=[*failures,gemini_ok_response()]) as call, \
         patch('src.llm_evaluator.time.sleep') as sleep,patch('src.llm_evaluator.random.uniform',return_value=0):
        reply,usage=adapter.request('Return JSON status ok')
    assert reply=={'status':'ok'} and usage['input_tokens']==10
    assert call.call_count==3 and adapter.last_attempts==3
    assert [x.args[0] for x in sleep.call_args_list]==[1,2]
    assert len(messages)==2 and 'attempt 3/3' in messages[-1]


def test_persistent_503_stops_and_explains_outage():
    from urllib.error import HTTPError
    from src.llm_evaluator import describe_error
    adapter=JudgeProvider('Gemini','gemini-3.8-flash','fake-key')
    failures=[HTTPError('https://example.test?key=never-display',503,'private response body',{},None) for _ in range(3)]
    with patch('urllib.request.urlopen',side_effect=failures) as call,patch('src.llm_evaluator.time.sleep'), \
         pytest.raises(HTTPError) as error:
        adapter.request('Return JSON')
    assert call.call_count==3
    message=describe_error('Gemini',error.value)
    assert '503' in message and '3 attempt' in message and 'temporarily' in message
    assert 'never-display' not in message and 'private response body' not in message


@pytest.mark.parametrize('code',[400,401,403,404,429])
def test_auth_model_and_quota_failures_are_not_retried(code):
    from urllib.error import HTTPError
    adapter=JudgeProvider('Gemini','gemini-3.8-flash','fake-key')
    with patch('urllib.request.urlopen',side_effect=HTTPError('https://example.test',code,'error',{},None)) as call, \
         patch('src.llm_evaluator.time.sleep') as sleep,pytest.raises(HTTPError):
        adapter.request('Return JSON')
    assert call.call_count==1 and not sleep.called


def test_long_retry_after_does_not_retry_early():
    from urllib.error import HTTPError
    adapter=JudgeProvider('Gemini','gemini-3.8-flash','fake-key')
    with patch('urllib.request.urlopen',side_effect=HTTPError('https://example.test',503,'busy',{'Retry-After':'120'},None)) as call, \
         patch('src.llm_evaluator.time.sleep') as sleep,pytest.raises(HTTPError):
        adapter.request('Return JSON')
    assert call.call_count==1 and not sleep.called
