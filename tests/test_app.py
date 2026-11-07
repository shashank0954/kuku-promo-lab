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
    app=AppTest.from_file('app.py',default_timeout=40).run()
    assert not app.exception
    assert any(x.label=='API key (session only)' for x in app.text_input)
    assert not any(x.label=='API key (session only)' for x in app.sidebar.text_input)

    assert len(app.tabs)==4
    app.button[0].click().run()
    assert not app.exception
    provider=next(x for x in app.selectbox if x.label=='Provider')
    provider.select('Gemini').run()
    assert not app.exception
    assert next(x for x in app.text_input if x.label=='Model name (editable)').value=='gemini-2.5-flash'
    next(x for x in app.text_input if x.label=='API key (session only)').input('test-not-a-real-key').run()
    assert not app.exception
    assert 'test-not-a-real-key' not in str(app.session_state['result'])
    # No network inference is triggered by selecting a provider.
    kind=next(x for x in app.selectbox if x.label=='Edit type')
    kind.select('mashup').run()
    assert not app.exception


def test_cloud_saved_results_without_confidential_sources(tmp_path):
    from unittest.mock import patch
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    st.cache_data.clear()
    try:
        with patch('run_pipeline.DEFAULT_INPUT', tmp_path / 'not-bundled'):
            app=AppTest.from_file('app.py',default_timeout=40).run()
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
