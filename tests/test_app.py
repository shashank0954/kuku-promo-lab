import io
import zipfile
import pytest
from pathlib import Path
from src.inputs import read_uploads
from run_pipeline import DEFAULT_INPUT

class Upload(io.BytesIO):
    def __init__(self,name,content):
        super().__init__(content);self.name=name

def test_txt_and_zip_uploads():
    if not DEFAULT_INPUT.exists():
        pytest.skip('Confidential source pack is not bundled')
    source=sorted(DEFAULT_INPUT.glob('*.txt'))[0]
    assert read_uploads([Upload(source.name,source.read_bytes())])[0].number==1
    pack=io.BytesIO()
    with zipfile.ZipFile(pack,'w') as z:
        z.writestr('nested/'+source.name,source.read_bytes())
        z.writestr('__MACOSX/ignored.txt','invalid')
    assert len(read_uploads([Upload('pack.zip',pack.getvalue())]))==1
    with pytest.raises(ValueError,match='Duplicate'):
        read_uploads([Upload(source.name,source.read_bytes()),Upload(source.name,source.read_bytes())])

def test_dashboard_load_run_and_provider_switch():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    assert not app.exception
    assert any(x.label=='API key (session only)' for x in app.text_input)
    assert not any(x.label=='API key (session only)' for x in app.sidebar.text_input)

    assert len(app.tabs)==4
    next(x for x in app.button if x.label=='Find promos').click().run()
    assert not app.exception

    provider=next(x for x in app.selectbox if x.label=='Provider')
    provider.select('Gemini').run()
    assert not app.exception
    assert next(x for x in app.text_input if x.label=='Model name (editable)').value=='gemini-3.5-flash-lite'
    next(x for x in app.text_input if x.label=='API key (session only)').input('test-not-a-real-key').run()
    assert not app.exception
    assert 'test-not-a-real-key' not in str(app.session_state['result'])
    # No network inference is triggered by selecting a provider.
    kind=next(x for x in app.selectbox if x.label=='Edit type')
    kind.select('mashup').run()
    assert not app.exception


def test_fresh_sample_run_replaces_saved_results():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    app.radio[0].set_value('Try a sample screenplay').run()
    next(x for x in app.button if x.label=='Find promos').click().run()
    assert not app.exception
    assert app.metric[0].value=='1'
    result=app.session_state['result']
    assert [e['episode'] for e in result['run']['episode_coverage']]==[101]
    assert result['promos'] and result['audit']['hard_failures']==[]
    assert all(s['episode']==101 for x in result['promos'] for s in x['segments'])


def test_api_connection_test_uses_selected_model_without_exporting_key():
    from streamlit.testing.v1 import AppTest
    from unittest.mock import patch
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    next(x for x in app.selectbox if x.label=='Provider').select('Gemini').run()
    next(x for x in app.text_input if x.label=='API key (session only)').input('fake-interview-key').run()
    with patch('src.llm_evaluator.JudgeProvider.request',return_value=({'status':'ok'},{'input_tokens':10,'output_tokens':4})) as request:
        next(x for x in app.button if x.label=='Test API connection').click().run()
    assert not app.exception and request.call_count==1
    assert any('API connection succeeded' in x.value for x in app.success)
    assert 'fake-interview-key' not in str(app.session_state['result'])


def test_cloud_saved_results_without_confidential_sources(tmp_path):
    from unittest.mock import patch
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    st.cache_data.clear()
    try:
        with patch('run_pipeline.DEFAULT_INPUT', tmp_path / 'not-bundled'):
            app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
            assert not app.exception
            assert len(app.tabs)==4
            assert app.metric[0].value=='50'
            assert app.radio[0].value=='Saved 50-episode playbook'
            episode=next(x for x in app.selectbox if x.label=='Episode')
            episode.select('Episode 25').run()
            assert not app.exception
            assert any('Full timeline requires' in x.value for x in app.info)
    finally:
        st.cache_data.clear()


def test_small_gemini_setup_selects_sample_and_one_candidate_without_api_call():
    from streamlit.testing.v1 import AppTest
    from unittest.mock import patch
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    next(x for x in app.selectbox if x.label=='Provider').select('Gemini').run()
    assert any('free standard text' in x.value for x in app.info)
    with patch('src.llm_evaluator.JudgeProvider.request') as request:
        next(x for x in app.button if x.label=='Prepare small Gemini test').click().run()
    assert not app.exception and request.call_count==0
    assert app.radio[0].value=='Try a sample screenplay'
    assert next(x for x in app.slider if x.label=='Maximum AI-judged finalists').value==1
    assert any('placeholder' in x.value for x in app.info)


def test_persistent_provider_outage_is_not_reported_as_success():
    from streamlit.testing.v1 import AppTest
    from unittest.mock import patch
    from urllib.error import HTTPError
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    next(x for x in app.selectbox if x.label=='Provider').select('Gemini').run()
    next(x for x in app.text_input if x.label=='API key (session only)').input('fake-key').run()
    with patch('src.llm_evaluator.JudgeProvider.request',side_effect=HTTPError('https://example.test',503,'busy',{},None)):
        next(x for x in app.button if x.label=='Test API connection').click().run()
    assert not app.exception
    assert any('503' in x.value and 'temporarily' in x.value for x in app.warning)
    assert not any('API connection succeeded' in x.value for x in app.success)
    assert any('connection has not succeeded' in x.value for x in app.info)


def test_flash_lite_alternative_can_prepare_small_test():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
    next(x for x in app.selectbox if x.label=='Provider').select('Gemini').run()
    next(x for x in app.selectbox if x.label=='Model preset').select('gemini-3.5-flash-lite').run()
    assert next(x for x in app.text_input if x.label=='Model name (editable)').value=='gemini-3.5-flash-lite'
    next(x for x in app.button if x.label=='Prepare small Gemini test').click().run()
    assert not app.exception and app.radio[0].value=='Try a sample screenplay'
    assert next(x for x in app.slider if x.label=='Maximum AI-judged finalists').value==1
