"""Bounded TXT/ZIP loading without filesystem extraction."""
import io
import zipfile
from pathlib import Path
from .parser import parse_text

def read_uploads(files):
    episodes=[];total_bytes=0
    for f in files:
        raw=f.getvalue();total_bytes+=len(raw)
        if total_bytes>20_000_000: raise ValueError('Upload limit: 20 MB total')
        if f.name.lower().endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                entries=[x for x in archive.infolist() if x.filename.lower().endswith('.txt') and not x.filename.startswith('__MACOSX/')]
                if len(entries)>500 or sum(x.file_size for x in entries)>20_000_000: raise ValueError('ZIP expands beyond 500 files / 20 MB')
                for entry in entries:
                    episodes.append(parse_text(archive.read(entry).decode('utf-8-sig'),Path(entry.filename).name))
        else: episodes.append(parse_text(raw.decode('utf-8-sig'),f.name))
    if not episodes: raise ValueError('No screenplay text files found')
    if len({e.number for e in episodes})!=len(episodes): raise ValueError('Duplicate episode numbers in upload')
    return sorted(episodes,key=lambda e:e.number)

