"""Bounded TXT/ZIP loading without filesystem extraction."""
import io
import re
import zipfile
from pathlib import Path
from .parser import parse_text

def parse_episode_selection(value,available):
    """Parse an explicit subset, rejecting unavailable episodes and unbounded ranges."""
    available=set(available)
    text=re.sub(r'\s*-\s*','-',value.strip().replace('–','-').replace('—','-'))
    if not text: raise ValueError('Enter episode numbers, for example 2, 5, 8-10.')
    selected=set()
    for token in re.split(r'[,;\s]+',text):
        if not token: continue
        match=re.fullmatch(r'(\d+)(?:-(\d+))?',token)
        if not match: raise ValueError(f'Invalid episode selection: {token}. Use numbers and ranges such as 2, 5, 8-10.')
        low=int(match[1]);high=int(match[2] or match[1])
        if low<1 or high<low: raise ValueError(f'Invalid episode range: {token}.')
        if high-low+1>len(available): raise ValueError(f'Range {token} includes episodes that are not in this input.')
        selected.update(range(low,high+1))
    if not selected: raise ValueError('Choose at least one episode.')
    missing=sorted(selected-available)
    if missing: raise ValueError('Not in this input: '+', '.join(map(str,missing[:15]))+'. Choose from the available episodes shown above.')
    return sorted(selected)

def read_uploads(files):
    episodes=[];total_bytes=0;expanded_bytes=0;file_count=0
    for f in files:
        raw=f.getvalue();total_bytes+=len(raw)
        if total_bytes>20_000_000: raise ValueError('Upload limit: 20 MB total')
        if f.name.lower().endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                entries=[x for x in archive.infolist() if x.filename.lower().endswith('.txt') and not x.filename.startswith('__MACOSX/')]
                if len(entries)>500 or sum(x.file_size for x in entries)>20_000_000: raise ValueError('ZIP expands beyond 500 files / 20 MB')
                expanded_bytes+=sum(x.file_size for x in entries);file_count+=len(entries)
                if expanded_bytes>20_000_000 or file_count>500: raise ValueError('Combined upload exceeds 500 screenplay files / 20 MB expanded')
                for entry in entries:
                    episodes.append(parse_text(archive.read(entry).decode('utf-8-sig'),Path(entry.filename).name))
        else:
            expanded_bytes+=len(raw);file_count+=1
            if expanded_bytes>20_000_000 or file_count>500: raise ValueError('Combined upload exceeds 500 screenplay files / 20 MB expanded')
            episodes.append(parse_text(raw.decode('utf-8-sig'),f.name))
    if not episodes: raise ValueError('No screenplay text files found')
    if len({e.number for e in episodes})!=len(episodes): raise ValueError('Duplicate episode numbers in upload')
    return sorted(episodes,key=lambda e:e.number)

