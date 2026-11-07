"""Kuku • script-to-promo editorial workbench."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.parser import parse_folder
from src.inputs import read_uploads
from src.llm_evaluator import MODELS,DEFAULT_WEIGHTS,DIMENSIONS
from src.economics import estimate,cost,RATES
from run_pipeline import execute,DEFAULT_INPUT,format_segments

st.set_page_config(page_title='Kuku | Promo Lab',page_icon='🎬',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>.block-container{padding-top:2rem;max-width:1450px}div[data-testid="stMetric"]{background:#141e2d;padding:16px;border-radius:12px} .hook{border-left:4px solid #21b879;padding-left:12px}.cut{border-left:4px solid #f76e70;padding-left:12px}</style>''',unsafe_allow_html=True)
st.caption('KUKU  /  GROWTH EDITORIAL WORKBENCH')
st.title('Find the moment. Leave them wanting more.')
st.write('Source-grounded promo cuts, ranked for a viewer who has never seen the show.')
APP_ROOT = Path(__file__).resolve().parent
SAVED_OUTPUT = APP_ROOT / 'raw_outputs/all_episodes_promos_ranked.json'

with st.expander('AI provider & API key', expanded=True):
    provider_col, model_col, key_col = st.columns(3)
    with provider_col:
        provider=st.selectbox('Provider',['Heuristic/Offline',*MODELS])
    with model_col:
        model=st.selectbox('Model preset',MODELS[provider]) if provider in MODELS else None
        if model: model=st.text_input('Model name (editable)',model)
        else: st.caption('Choose Gemini, OpenAI or Anthropic to use your own model.')
    with key_col:
        key=st.text_input('API key (session only)',type='password',key=f'api_key_{provider}',
                          help='Used only for the selected provider. Keys are never written into exported results. A configured environment key also works.')
    if provider=='Heuristic/Offline':
        st.caption('Offline mode selected. To use an API key, choose Gemini, OpenAI or Anthropic above.')
    else:
        st.caption('Upload screenplay TXT files or a ZIP in the sidebar, then click Find promos to run with this provider. Saved results stay unchanged until you run again.')
    if provider=='Anthropic': st.caption('Claude 3.5 presets are legacy and may be retired. Use an available model ID; API errors are reported with offline fallback.')

@st.cache_data
def preload():
    if DEFAULT_INPUT.exists(): return parse_folder(DEFAULT_INPUT)
    return []


with st.sidebar:
    st.header('Run your show')
    saved_label = 'Preloaded 50 episodes' if DEFAULT_INPUT.exists() else 'Saved 50-episode playbook'
    options = [saved_label, 'Upload screenplay files'] if DEFAULT_INPUT.exists() or SAVED_OUTPUT.exists() else ['Upload screenplay files']
    source=st.radio('Input',options)
    uploads=st.file_uploader('TXT files or a ZIP pack',type=['txt','zip'],accept_multiple_files=True) if source.startswith('Upload') else []
    minimum,maximum=st.slider('Total duration (seconds)',20,60,(20,60))
    st.caption('Rubric weights (normalized on run)')
    weights={k:st.slider(k.replace('_score','').replace('_',' ').title(),0,100,int(v*100),key=k) for k,v in DEFAULT_WEIGHTS.items()}
    budget=st.slider('Maximum AI-judged finalists',0,20,8,help='Remaining candidates keep labeled heuristic scores.')
    run=st.button('Find promos',type='primary',use_container_width=True)
    st.caption('Offline is reproducible and free. AI calls send shortlisted script excerpts to the selected provider.')

try:
    episodes=read_uploads(uploads) if source.startswith('Upload') and uploads else (preload() if not source.startswith('Upload') else [])
except Exception as exc:
    st.error(f'Input validation: {exc}');episodes=[]

if run:
    if not episodes: st.error('Upload TXT screenplay files or their ZIP pack to run the pipeline. Saved results can be browsed without the source files.')
    elif not sum(weights.values()): st.error('At least one rubric weight must be positive.')
    else:
        with st.spinner(f'Parsing, slicing, scoring and auditing {len(episodes)} episodes…'):
            try:
                st.session_state['result']=execute(episodes,provider,model,key,minimum,maximum,weights,budget)
                st.session_state['episodes']=episodes
                st.session_state['run_input']=source
            except Exception as exc: st.error(f'Run failed: {type(exc).__name__}: {exc}')

if 'result' not in st.session_state and not source.startswith('Upload'):
    if SAVED_OUTPUT.exists():
        st.session_state['result']=json.loads(SAVED_OUTPUT.read_text());st.session_state['episodes']=episodes;st.session_state['run_input']=source
    elif episodes:
        st.session_state['result']=execute(episodes,'Heuristic/Offline');st.session_state['episodes']=episodes;st.session_state['run_input']=source

if 'result' not in st.session_state:
    st.info('Load screenplay files and choose Find promos to create your playbook.');st.stop()
r=st.session_state['result'];eps=st.session_state['episodes'];lookup={e.number:e for e in eps}
coverage={e['episode']: e for e in r['run']['episode_coverage']}
if not eps:
    st.info('Showing saved results from all 50 episodes. Upload the original TXT files or ZIP to rerun the pipeline and inspect full verbatim timelines. Source screenplays are not bundled with the deployment.')
if st.session_state.get('run_input')!=source: st.info('Showing the previous run. Choose Find promos to analyze the selected input.')
metrics=st.columns(4)
for col,label,value in zip(metrics,['Episodes analyzed','Ranked cuts','Source checks passed','Run time'],[r['run']['episode_count'],len(r['promos']),f"{r['audit']['passed']}/{r['audit']['hard_checks']}",f"{r['run']['elapsed_seconds']:.2f}s"]): col.metric(label,value)
st.caption(f"Results: {r['run']['provider']['provider']} · {r['run']['beat_count']:,} source beats · Scores are editorial estimates, not measured ad performance.")
for warning in r['run']['provider']['errors']: st.warning(warning)

def timeline(item):
    for s in item['segments']:
        st.markdown(f"**Episode {s['episode']} · {s['start_timestamp']} → {s['end_timestamp']}**")
        if s['episode'] not in lookup:
            st.info('Full timeline requires the source screenplay. Choose Upload screenplay files, upload the scripts, and click Find promos.')
            continue
        st.caption('Green = overlaps opening 3 seconds. Red = overlaps final 4 seconds. Original full beat text is preserved; visual beats may extend beyond the selected cut.')
        rows=[]
        for b in lookup[s['episode']].excerpt(s['start'],s['end']):
            rows.append({'Window':'🟩 HOOK' if b['start']<s['start']+3 else ('🟥 CUT' if b['end']>s['end']-4 else ''),
                         'Start':b['start_timestamp'],'End':b['end_timestamp'],'Track':b['kind'],'Speaker / delivery':b['speaker'],'Verbatim source':b['text']})
        frame=pd.DataFrame(rows)
        def shade(row):
            color='#123d2b' if row['Window'].startswith('🟩') else '#51242a' if row['Window'].startswith('🟥') else ''
            return [f'background-color: {color}' if color else '' for _ in row]
        st.dataframe(frame.style.apply(shade,axis=1),hide_index=True,use_container_width=True)
        with st.container():
            st.caption('Unified audiovisual slices (simultaneous tracks)')
            for t in lookup[s['episode']].timeline:
                if t['start']<s['end'] and t['end']>s['start']:
                    st.text(f"{max(s['start'],t['start']):.2f}–{min(s['end'],t['end']):.2f}s | {', '.join(t['beat_ids']) or 'silence / no source event'}")

def detail(item):
    st.subheader(f"#{item['rank']} · {format_segments(item)}")
    st.write(item['posting_strategy']);st.caption(item['posting_reason'])
    a,b=st.columns(2);a.success('FIRST 3s · '+item['hook_text']);b.error('CLIFFHANGER · '+item['cliffhanger_text'])
    st.write(item['why_it_works']);st.caption(item['ranking_rationale'])
    st.bar_chart(pd.DataFrame({'Score':item['scores']}))
    if item['editorial_flags']: st.warning('Editor review: '+'; '.join(item['editorial_flags']))
    with st.expander('Verbatim script timeline viewer'): timeline(item)

tabs=st.tabs(['01 · Ranked playbook','02 · Episode explorer','03 · Where it fails','04 · Scale & economics'])
with tabs[0]:
    left,right=st.columns(2)
    tier=left.multiselect('Posting tiers',sorted({x['posting_strategy'] for x in r['promos']}))
    threshold=right.slider('Minimum composite score',0,100,0)
    kind=st.selectbox('Edit type',['All','single','mashup'])
    items=[x for x in r['promos'] if (not tier or x['posting_strategy'] in tier) and x['composite_score']>=threshold and (kind=='All' or x['kind']==kind)]
    rows=[dict(Rank=x['rank'],Priority=x['posting_strategy'],Episodes=', '.join(str(s['episode']) for s in x['segments']),Cuts=format_segments(x),Seconds=x['duration'],Score=x['composite_score'],Hook=x['hook_text'],Cliffhanger=x['cliffhanger_text'],Why=x['why_it_works'],**x['scores']) for x in items]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    if items:
        labels=[f"#{x['rank']} · {format_segments(x)}" for x in items]
        chosen=st.selectbox('Inspect a promo',labels)
        detail(items[labels.index(chosen)])
    st.download_button('Download complete ranked JSON',json.dumps(r,ensure_ascii=False,indent=2),file_name='promos_ranked.json',mime='application/json')
    if rows: st.download_button('Download filtered editor CSV',pd.DataFrame(rows).to_csv(index=False),file_name='promo_playbook.csv',mime='text/csv')
with tabs[1]:
    number=int(st.selectbox('Episode',[f'Episode {n}' for n in sorted(coverage)]).split()[-1])
    st.write(coverage[number]['logline'])
    episode_items=[x for x in r['promos'] if any(s['episode']==number for s in x['segments'])]
    st.caption(f'{len(episode_items)} candidates; episodes with no qualifying windows are retained in coverage.')
    if episode_items:
        labels=[f"#{x['rank']} · {format_segments(x)}" for x in episode_items]
        selected=st.selectbox('Candidate',labels)
        detail(episode_items[labels.index(selected)])
    else: st.info('No candidate met retrieval and duration constraints. An editor can inspect the source rather than force a weak promo.')
with tabs[2]:
    st.write(r['audit']['method']);st.json({k:v for k,v in r['audit'].items() if k!='failure_examples'},expanded=False)
    strong,weak=st.columns(2)
    with strong:
        st.subheader('Fewer automated review flags')
        clean=[x for x in r['promos'] if not x['editorial_flags']]
        if clean:
            st.write(format_segments(clean[0]));st.success(clean[0]['hook_text']);st.write(clean[0]['ranking_rationale'])
        st.caption('“Stronger” means fewer automated flags; it does not mean a human has approved the footage.')
    with weak:
        st.subheader('Borderline / rejected baselines')
        failures=r['audit']['failure_examples']
        if failures:
            fid=st.selectbox('Real failure example',[x['id'] for x in failures])
            x=next(x for x in failures if x['id']==fid);st.write(format_segments(x));st.warning('; '.join(x['categories']));st.write(x['hook']);st.write('Cut: '+x['cut']);st.info(x['human_fix'])
    st.caption('Known development error: substring matching interpreted “hang” inside “cliffhanger” as an execution threat. Word boundaries and a music-only cap corrected it. Tear-streaked faces were also incorrectly treated as physical tearing.')
with tabs[3]:
    st.subheader('A bounded AI shortlist, transparent assumptions')
    a,b,c=st.columns(3)
    shortlist=a.number_input('Finalists / show',0,500,8)
    tokens=b.number_input('Input tokens / finalist (estimate)',100,10000,1800)
    output=c.number_input('Output tokens / finalist (estimate)',10,2000,160)
    a,b=st.columns(2)
    in_rate=a.number_input('USD / million input tokens',value=.30,min_value=0.0,format='%.3f')
    out_rate=b.number_input('USD / million output tokens',value=2.50,min_value=0.0,format='%.3f')
    raw_tokens=st.number_input('Full-script input tokens / show (estimated from this source)',min_value=1,value=max(1,r['run']['raw_script_token_estimate']))
    passes=st.slider('Naive full-script passes',1,10,3)
    costs=estimate(shortlist,tokens,output,in_rate,out_rate,raw_tokens,passes)
    a,b,c=st.columns(3)
    a.metric('Hybrid estimate / show',f"${costs['hybrid_usd']:.5f}")
    b.metric('Naive / same rates',f"${costs['naive_same_model_usd']:.4f}")
    c.metric('Naive / premium reference',f"${costs['naive_premium_usd']:.4f}")
    st.caption('Reference: Gemini 2.5 Flash $0.30 input / $2.50 output per million; premium scenario $2.50 / $10. Editable estimates exclude hosting, retries, taxes and human review. $1.50+ requires the displayed volume/model assumptions; it is not universal.')
    shows=st.slider('Shows / week',1,1000,200)
    latency=st.slider('AI latency / batch (seconds; assumption)',1,60,8)
    batches=(shortlist+3)//4
    st.write(f"At {shows} shows/week: estimated AI spend **${shows*costs['hybrid_usd']:.2f}/week**; sequential AI time **{batches*latency}s/show**, plus local parsing/scoring. Workers can parallelize shows within rate limits.")
    st.subheader('Actual run telemetry')
    st.json(r['run']['provider']);st.caption('Offline usage and cost are zero. Live provider tokens come from API usage fields; the cost is calculated at reference rates, not an invoice. Mixed AI / heuristic candidates are labeled individually.')
    st.markdown('[Google pricing](https://ai.google.dev/gemini-api/docs/pricing) · [OpenAI pricing](https://openai.com/api/pricing/) · [Anthropic model lifecycle](https://platform.claude.com/docs/en/about-claude/model-deprecations)')
