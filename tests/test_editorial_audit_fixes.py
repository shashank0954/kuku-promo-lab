"""Audit-specific development regressions, not independent human validation."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import pytest
from src.parser import parse_folder
from src.candidate_generator import hook,cliff,physical_conflict,segment,make_candidate
from src.llm_evaluator import evaluate_offline,MODELS
from run_pipeline import execute,DEFAULT_INPUT


def beat(text,kind='CAMERA',speaker=None):
    b=deepcopy(parse_folder(Path(__file__).resolve().parents[1]/'examples')[0].beats[0])
    b.text=text;b.kind=kind;b.speaker=speaker or kind
    return b

@pytest.mark.parametrize('text',[
 'He lifts a kettle from the hearth chain.', 'A chandelier chain sways.',
 'She fastens the door chain.', 'Her delicate gold chain catches the light.',
 'A silver locket chain rests against her gown.', 'His watch chain gleams.',
 'She holds up her burning lantern.', 'A dripping candle burning on a table.',
 'The burning candle flickers.', 'A burning hearth warms the room.',
 'She sits beside the burning fireplace.', 'My chest is burning.',
 'A fever is burning through him.', 'Juliana kneels beside a washbasin.',
 'She is kneeling on the ground pulling weeds.', 'She kneels amidst the ruined soil.',
])
def test_benign_objects_and_postures_are_not_violent_hooks(text):
 assert physical_conflict(text)==0
 assert hook(beat(text))==0

@pytest.mark.parametrize('text',[
 'She is chained to the wall.', 'Iron chains cut into her skin.',
 'A guard drags her away in shackles.', 'He snaps the chain around her neck.',
 'He grabs the chain around her neck.', 'Burn it.', 'Burn the ledger.',
 'A burned page lies in her hands.', 'Her burned skin blisters.',
 'He forced her to kneel.', 'You will make me kneel.',
 'She kneels beside her seated father, begging.',
 'He is laughing hysterically at her kneeling form.', 'He drops to one knee.',
])
def test_actual_restraint_arson_and_humiliation_remain_hooks(text):
 assert physical_conflict(text)>0
 assert hook(beat(text))>=60

@pytest.mark.parametrize('text',['What?','Who?','Of them?','Not yet?','Shall we?','What is it?','You see?','How long?'])
def test_filler_endpoints_are_capped(text):assert cliff(beat(text,'DIALOGUE'))<=35

@pytest.mark.parametrize('text',["You're the Duke?",'Who did this?','Why are you holding her hand?',
 'Because he is marrying me.',"Do you think she will actually be executed?",
 'Then why are you so desperate to make me kneel?','Your inheritance is revoked.'])
def test_substantive_questions_reveals_and_threats_survive(text):assert cliff(beat(text,'DIALOGUE'))>=65


def test_character_labels_do_not_create_wedding_theme():
 from src.editorial_explanations import content_text,classify_theme
 b=beat('The Former Groom enters the study.','ACTION')
 text=content_text([b,beat('What is it?','DIALOGUE','THE FORMER GROOM (Cold)')])
 assert 'groom' not in text.lower()
 assert classify_theme(text)!='Altar Betrayal & Humiliation'


def test_camera_betrayal_description_is_not_a_declarative_accusation():
 assert cliff(beat('Close-up of her as betrayal strikes deep.'))<65


@pytest.fixture(scope='module')
def source():
 if not DEFAULT_INPUT.exists():pytest.skip('Confidential pack not distributed')
 return parse_folder(DEFAULT_INPUT)


def test_e9_resolution_pivot_is_rejected_and_in_failure_audit(source):
 ep=next(e for e in source if e.number==9)
 c=evaluate_offline(make_candidate([segment(ep,40.8,87.4)],'E9-40.8-87.4'),source)
 assert hook(next(b for b in ep.beats if b.id=='9:32'))==0
 assert c['scores']['cliffhanger_score']<=35
 assert any(x['code']=='resolved_mid_clip' and x['evidence'] for x in c['heuristic_concerns'])
 assert c['decision']['status']=='rejected'
 assert c['theme']!='Altar Betrayal & Humiliation'
 r=execute(source,'Heuristic/Offline')
 assert any(x['id']==c['id'] and 'resolved_mid_clip' in x['concern_codes'] for x in r['audit']['failure_examples'])


def test_final_singles_cap_coverage_and_whole_boundaries(source):
 r=execute(source,'Heuristic/Offline')
 singles=Counter(x['segments'][0]['episode'] for x in r['promos'] if x['kind']=='single')
 assert max(singles.values())<=3
 represented=sum(x['candidates']>0 for x in r['run']['episode_coverage'])
 assert 35<=represented<=45
 assert not r['audit']['hard_failures']
 assert all(x['scores']['hook_3s_score']>=60 for x in r['promos'])


def test_model_default_is_current_while_legacy_compatibility_remains():
 assert MODELS['Gemini'][0]=='gemini-3.5-flash-lite'
 assert {'gemini-3.8-flash','gemini-2.5-flash','gemini-2.5-pro','gemini-2.0-flash'}<=set(MODELS['Gemini'])
