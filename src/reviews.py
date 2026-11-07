"""Portable review annotations, separate from immutable pipeline output."""
import hashlib
import json

def fingerprint(episodes,result):
    payload=[(e.number,[(b.id,b.start,b.end,b.text) for b in e.beats]) for e in sorted(episodes,key=lambda e:e.number)] if episodes else result.get('run',{}).get('episode_coverage',[])
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()

def identity(scope,item):
    return hashlib.sha256(json.dumps([scope,[(s['episode'],s['start_timestamp'],s['end_timestamp']) for s in item['segments']]]).encode()).hexdigest()

def export_reviews(scope,decisions):return json.dumps(dict(version=1,input_fingerprint=scope,decisions=decisions),indent=2)

def import_reviews(data,scope,items):
    obj=json.loads(data)
    if obj.get('version')!=1 or obj.get('input_fingerprint')!=scope:raise ValueError('Review file belongs to a different input')
    allowed={identity(scope,x) for x in items};decisions=obj.get('decisions')
    if not isinstance(decisions,dict):raise ValueError('Invalid decisions')
    for key,value in decisions.items():
        if key not in allowed or not isinstance(value,dict) or set(value)!={'script','footage','notes'}:raise ValueError('Unknown candidate or invalid review fields')
        if value['script'] not in ('Unreviewed','Approve','Reject') or value['footage'] not in ('Unreviewed','Approve','Reject') or not isinstance(value['notes'],str):raise ValueError('Invalid review decision')
    return decisions
