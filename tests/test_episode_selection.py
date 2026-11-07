from pathlib import Path
from unittest.mock import patch
import pytest
from src.inputs import parse_episode_selection
from src.parser import parse_text
from run_pipeline import execute


def demo_episodes():
    source=(Path(__file__).resolve().parents[1]/'examples/demo_screenplay.txt').read_text()
    return [parse_text(source.replace('EPISODE NUMBER: Episode 101',f'EPISODE NUMBER: Episode {n}'),f'demo-{n}.txt') for n in (2,5,25)]


@pytest.mark.parametrize('text,expected',[
    ('2, 5, 8-10',[2,5,8,9,10]),
    ('10; 2 5, 2',[2,5,10]),
    ('8 – 10',[8,9,10]),
])
def test_manual_episode_numbers_and_ranges(text,expected):
    assert parse_episode_selection(text,range(1,51))==expected


@pytest.mark.parametrize('text',['','5-2','2,99','abc','1-999999999','0','-2'])
def test_invalid_or_unavailable_selections_are_rejected(text):
    with pytest.raises(ValueError):parse_episode_selection(text,[2,5,25])


def test_pipeline_uses_only_selected_episodes_and_allows_explicit_distant_mashups():
    result=execute(demo_episodes(),'Heuristic/Offline',episode_numbers=[2,25])
    assert result['run']['loaded_episode_count']==3
    assert result['run']['episode_count']==2
    assert result['run']['selected_episode_numbers']==[2,25]
    assert [e['episode'] for e in result['run']['episode_coverage']]==[2,25]
    assert result['promos'] and not result['audit']['hard_failures']
    assert all(s['episode'] in (2,25) for item in result['promos']+result['rejected_candidates'] for s in item['segments'])
    assert any({s['episode'] for s in item['segments']}=={2,25} for item in result['promos'] if item['kind']=='mashup')


def test_episode_selection_dashboard_reruns_without_reuploading_input():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    with patch('src.parser.parse_folder',return_value=demo_episodes()):
        app.radio[0].set_value('Try a sample screenplay').run()
        next(x for x in app.selectbox if x.label=='Episodes to analyze').select('Enter episode numbers').run()
        next(x for x in app.text_input if x.label=='Episode numbers').input('2,25').run()
        next(x for x in app.button if x.label=='Find promos').click().run()
        assert not app.exception
        assert app.session_state['result']['run']['selected_episode_numbers']==[2,25]
        next(x for x in app.text_input if x.label=='Episode numbers').input('5').run()
        assert any('previous run' in x.value for x in app.info)
        next(x for x in app.button if x.label=='Find promos').click().run()
        assert not app.exception
        assert app.session_state['result']['run']['selected_episode_numbers']==[5]
        assert app.session_state['result']['run']['loaded_episode_count']==3


def test_invalid_selection_never_runs_pipeline():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    with patch('src.parser.parse_folder',return_value=demo_episodes()):
        app.radio[0].set_value('Try a sample screenplay').run()
        next(x for x in app.selectbox if x.label=='Episodes to analyze').select('Enter episode numbers').run()
        next(x for x in app.text_input if x.label=='Episode numbers').input('99').run()
        with patch('run_pipeline.execute') as pipeline:
            next(x for x in app.button if x.label=='Find promos').click().run()
        assert not app.exception and not pipeline.called
        assert any('Not in this input' in x.value for x in app.error)


def test_episode_picker_runs_only_checked_episodes():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    with patch('src.parser.parse_folder',return_value=demo_episodes()):
        app.radio[0].set_value('Try a sample screenplay').run()
        next(x for x in app.selectbox if x.label=='Episodes to analyze').select('Pick from list').run()
        next(x for x in app.multiselect if x.label=='Select episodes').set_value([2,25]).run()
        next(x for x in app.button if x.label=='Find promos').click().run()
        assert not app.exception
        assert app.session_state['result']['run']['selected_episode_numbers']==[2,25]
