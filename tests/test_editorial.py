import copy,json
import pytest
from src.editorial_policy import decide,ordering,judging_sample,validate_assessment,ASSESSMENTS
from src.reviews import identity,export_reviews,import_reviews
from scripts.evaluate_frozen import metrics

def item(id='a',score=70):
 return dict(id=id,scores=dict(hook_3s_score=score,cliffhanger_score=score,standalone_clarity_score=score),composite_score=score,heuristic_concerns=[],uncertainty=['supported by script timing'],segments=[dict(episode=1,start_timestamp='00:00.00',end_timestamp='00:20.00')])

def test_policy_separates_hard_concerns_uncertainty():
 x=item();assert decide(x)['status']=='recommended'
 x['uncertainty']=['uncertain within a long source beat'];assert decide(x)['status']=='review_required'
 assert decide(x,['Mid-dialogue'])['status']=='rejected'
 x['heuristic_concerns']=[dict(code='resolved',reason='Recovered')];assert not decide(x)['eligible']

def test_mixed_scores_do_not_replace_ranking():
 a,b=item('a',80),item('b',60);b['ai_scores']={'hook':100};b['ai_composite_score']=100
 assert sorted([b,a],key=ordering)[0]['id']=='a'

def test_budget_has_borderline_and_is_deterministic():
 xs=[item(str(n),v) for n,v in enumerate([99,98,97,96,55,30])]
 sample=judging_sample(xs,3)
 assert len(sample)==3 and xs[4] in sample and sample==judging_sample(list(reversed(xs)),3)

def test_unsupported_ai_evidence():
 class E: number=1;beats=[]
 assessment={k:dict(text='Claim',evidence=['1:999'],verdict='supported') for k in ASSESSMENTS}
 x=item();x['segments'][0].update(start=0,end=20)
 with pytest.raises(ValueError,match='Unsupported'):validate_assessment(assessment,x,[E()])

def test_portable_scoped_reviews():
 x=item();uid=identity('input',x);d={uid:dict(script='Approve',footage='Unreviewed',notes='Check onset')}
 assert import_reviews(export_reviews('input',d),'input',[x])==d
 with pytest.raises(ValueError):import_reviews(export_reviews('input',d),'different',[x])
 y=copy.deepcopy(x);y['segments'][0]['end_timestamp']='00:21.00'
 with pytest.raises(ValueError):import_reviews(export_reviews('input',d),'input',[y])

def test_metrics_pending_and_real_denominators():
 a,b=item('a',80),item('b',60)
 for x in (a,b):x['decision']=decide(x)
 cases=[{'candidate':a},{'candidate':b}];pred={'a':a,'b':b}
 assert metrics(cases,pred)['status']=='pending human labels'
 labels=[dict(candidate_id='a',human_accept='yes',reviewer='Human'),dict(candidate_id='b',human_accept='no',reviewer='Human')]
 m=metrics(cases,pred,labels,[dict(candidate_a='a',candidate_b='b',preferred='a',reviewer='Human')])
 assert m['acceptance_precision']==.5 and m['pairwise_agreement']==1 and m['pairwise_n']==1
 with pytest.raises(ValueError):metrics(cases,pred,[dict(candidate_id='a',human_accept='yes',reviewer='')])

def test_ai_answer_veto_and_insufficient_review():
 x=item();x['ai_assessment']={k:dict(text='Finding',evidence=['1:1'],verdict='supported') for k in ASSESSMENTS};x['ai_assessment']['already_answered']['verdict']='yes'
 assert decide(x)['status']=='rejected'
 x['ai_assessment']['already_answered']['verdict']='no';x['ai_assessment']['continuity']['verdict']='concern'
 assert decide(x)['status']=='review_required'

def test_dashboard_review_persists_across_reruns():
 from pathlib import Path
 from streamlit.testing.v1 import AppTest
 app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
 selector=next(x for x in app.multiselect if x.label=='Compare up to two promos')
 selector.select(selector.options[0]).run()
 next(x for x in app.selectbox if x.label=='Script decision').select('Approve').run()
 next(x for x in app.text_area if x.label=='Editor notes').input('Verify first spoken word').run()
 app.run()
 assert not app.exception
 assert next(x for x in app.selectbox if x.label=='Script decision').value=='Approve'
 assert next(x for x in app.selectbox if x.label=='Footage decision').value=='Unreviewed'
 assert next(x for x in app.text_area if x.label=='Editor notes').value=='Verify first spoken word'
