"""Render the designed PDF, page previews and visual playbook with local Chrome."""
import base64
import json
import hashlib
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request
from websockets.sync.client import connect

ROOT=Path(__file__).resolve().parents[1]
CHROME=os.getenv('CHROME_BIN') or shutil.which('google-chrome') or shutil.which('chromium') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

class CDP:
    def __init__(self,url):self.ctx=connect(url,max_size=30_000_000);self.ws=self.ctx.__enter__();self.counter=0
    def close(self):self.ctx.__exit__(None,None,None)
    def command(self,method,params=None):
        self.counter+=1;self.ws.send(json.dumps(dict(id=self.counter,method=method,params=params or {})))
        while True:
            message=json.loads(self.ws.recv(timeout=25))
            if message.get('id')==self.counter:
                if 'error' in message:raise RuntimeError(message['error'])
                return message.get('result',{})
    def evaluate(self,expression):
        result=self.command('Runtime.evaluate',{'expression':expression,'returnByValue':True})
        if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'])
        return result['result'].get('value')
    def wait_for(self,expression,seconds=25):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            if self.evaluate(expression):return
            time.sleep(.15)
        raise TimeoutError('Browser content did not become ready')


def main():
    with tempfile.TemporaryDirectory(prefix='kuku-visual-browser-',dir='/private/tmp' if Path('/private/tmp').exists() else None) as profile:
        log=open(Path(profile)/'chrome.log','w')
        process=subprocess.Popen([CHROME,'--headless=new','--disable-gpu','--disable-background-networking','--no-first-run','--no-default-browser-check',f'--user-data-dir={profile}','--remote-debugging-port=0','about:blank'],stdout=subprocess.DEVNULL,stderr=log)
        browser=None
        try:
            port_file=Path(profile)/'DevToolsActivePort'
            for _ in range(200):
                if port_file.exists():break
                time.sleep(.1)
            if not port_file.exists():
                log.flush()
                raise RuntimeError('Chrome debugger did not start: '+(Path(profile)/'chrome.log').read_text()[-2500:])
            port=int(port_file.read_text().splitlines()[0])
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list') as r:targets=json.load(r)
            browser=CDP(next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'))
            browser.command('Page.enable')
            browser.command('Emulation.setDeviceMetricsOverride',{'width':794,'height':1123,'deviceScaleFactor':1,'mobile':False})
            browser.command('Page.navigate',{'url':(ROOT/'SOLUTION_DOC.html').as_uri()})
            browser.wait_for("document.readyState==='complete' && document.querySelectorAll('.page').length===2 && [...document.images].every(i=>i.complete&&i.naturalWidth>0)")
            browser.command('Emulation.setEmulatedMedia',{'media':'print'})
            fit=browser.evaluate("[...document.querySelectorAll('.page')].map(p=>({bottom:p.querySelector('.flow').getBoundingClientRect().bottom,footer:p.querySelector('.footer').getBoundingClientRect().top}))")
            if any(p['bottom']>p['footer']-10 for p in fit):raise RuntimeError(f'Solution content overlaps footer: {fit}')
            pdf=browser.command('Page.printToPDF',{'printBackground':True,'preferCSSPageSize':True,'displayHeaderFooter':False})
            (ROOT/'SOLUTION_DOC.pdf').write_bytes(base64.b64decode(pdf['data']))
            boxes=browser.evaluate("[...document.querySelectorAll('.page')].map(p=>{let r=p.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1.5}})")
            for i,box in enumerate(boxes,1):
                browser.evaluate(f"[...document.querySelectorAll('.page')].forEach((p,j)=>p.style.display=j==={i-1}?'block':'none');window.scrollTo(0,0);true")
                box=browser.evaluate("(()=>{let r=document.querySelector('.page:not([style*=\"none\"])').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1.5}})()")
                shot=browser.command('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True,'clip':box})
                (ROOT/f'assets/solution_page_{i}.png').write_bytes(base64.b64decode(shot['data']))
            print('Solution PDF and two PNG previews rendered; both pages fit above their footers.')
            browser.evaluate("document.querySelectorAll('.page').forEach(p=>p.style.display='');true")
            browser.command('Emulation.setEmulatedMedia',{'media':''})
            browser.command('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
            browser.command('Page.navigate',{'url':(ROOT/'deliverables/visual_playbook.html').as_uri()})
            expected=json.loads((ROOT/'deliverables/visual_source.json').read_text())['promos']
            browser.wait_for(f"document.readyState==='complete' && document.querySelectorAll('.webcard').length==={expected}")
            assert browser.evaluate("document.querySelector('#count').textContent").startswith(str(expected))
            browser.evaluate("document.querySelector('#episode').value='25';document.querySelector('#episode').dispatchEvent(new Event('input'));true")
            assert browser.evaluate("document.querySelectorAll('.webcard:not([hidden])').length")>0
            assert browser.evaluate("[...document.querySelectorAll('.webcard:not([hidden])')].every(c=>c.dataset.episodes.split(',').includes('25'))")
            browser.evaluate("document.querySelector('#episode').value='';document.querySelector('#episode').dispatchEvent(new Event('input'));true")
            shot=browser.command('Page.captureScreenshot',{'format':'png'})
            (ROOT/'assets/playbook_preview.png').write_bytes(base64.b64decode(shot['data']))
            print('Visual playbook rendered; episode filter verified in the browser.')
            source_path=ROOT/'raw_outputs/all_episodes_promos_ranked.json'
            source_hash=hashlib.sha256(source_path.read_bytes()).hexdigest()
            assert source_hash==json.loads((ROOT/'deliverables/visual_source.json').read_text())['source_sha256'],'Rebuild the visual HTML for the current raw snapshot first.'
            outputs=[ROOT/'SOLUTION_DOC.pdf',ROOT/'SOLUTION_DOC.html',ROOT/'deliverables/visual_playbook.html',ROOT/'deliverables/visual_source.json',*sorted((ROOT/'assets').iterdir())]
            manifest={'source_sha256':source_hash,'presentation_only':True,'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs if p.is_file()}}
            (ROOT/'deliverables/visual_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')



        finally:
            if browser:
                try:browser.close()
                except Exception:pass
            process.terminate()
            try:process.wait(timeout=8)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            log.close()

if __name__=='__main__':main()
