import json
from pathlib import Path
from unittest.mock import patch
import pytest
from src.llm_evaluator import JudgeProvider,NoCredentialRedirect,redact_secret,describe_error
from urllib.request import Request
from urllib.error import HTTPError

def test_provider_redirects_never_forward_credentials():
 req=Request('https://api.openai.com/v1/chat/completions',headers={'Authorization':'Bearer fake-secret'})
 with pytest.raises(HTTPError):NoCredentialRedirect().redirect_request(req,None,302,'redirect',{},'https://attacker.test')

@pytest.mark.parametrize('model',['../evil','x?key=secret','https://attacker.test','x\nHeader: value'])
def test_model_cannot_inject_url(model):
 with pytest.raises(ValueError):JudgeProvider('Gemini',model,'fake').build_request('test')

def test_secret_reflection_and_error_redaction():
 secret='fake-secret-for-test'
 assert secret not in json.dumps(redact_secret({'reply':[secret],'key-'+secret:secret},secret))
 assert secret not in describe_error('Gemini',ValueError(secret))

def test_key_clear_and_session_isolation():
 from streamlit.testing.v1 import AppTest
 a=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
 next(x for x in a.selectbox if x.label=='Provider').select('Gemini').run()
 next(x for x in a.text_input if x.label=='API key (session only)').input('fake-secret-for-test').run()
 b=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=40).run()
 next(x for x in b.selectbox if x.label=='Provider').select('Gemini').run()
 assert next(x for x in b.text_input if x.label=='API key (session only)').value==''
 next(x for x in a.button if x.label=='Clear API keys from this session').click().run()
 assert next(x for x in a.text_input if x.label=='API key (session only)').value==''
 assert not a.exception and not b.exception
