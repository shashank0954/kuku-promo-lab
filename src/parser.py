"""Lossless source beats plus half-open, non-overlapping audiovisual slices."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import re

TS = r'\d+:\d{2}\.\d+'

def seconds(value):
    m, s = value.strip('() ').split(':')
    return round(int(m)*60 + float(s), 3)

def timestamp(value):
    return f'{int(value)//60:02d}:{value%60:05.2f}'

@dataclass
class Beat:
    id: str
    kind: str
    speaker: str
    start: float
    end: float
    start_timestamp: str
    end_timestamp: str
    text: str
    scene: str

@dataclass
class Scene:
    id: str
    heading: str
    start: float
    end: float
    beats: list = field(default_factory=list)

@dataclass
class Episode:
    number: int
    filename: str
    logline: str
    continuity: str
    scenes: list
    beats: list
    timeline: list
    warnings: list = field(default_factory=list)

    def safe(self, time):
        # Camera/action may span edits, but an audible utterance must remain whole.
        return not any(b.kind == 'DIALOGUE' and b.start < time < b.end for b in self.beats)

    def boundary(self, time, side):
        return any(getattr(b, side) == time for b in self.beats) and self.safe(time)

    def excerpt(self, start, end):
        return [asdict(b) for b in self.beats if b.start < end and b.end > start]


def parse_text(text, filename='upload.txt'):
    def meta(label):
        match = re.search(rf'^{label}:\s*(.*)$', text, re.M)
        if not match: raise ValueError(f'{filename}: missing {label}')
        return match.group(1)
    number = int(re.search(r'\d+', meta('EPISODE NUMBER')).group())
    if '--- SCRIPT START ---' not in text or '--- SCRIPT END ---' not in text:
        raise ValueError(f'{filename}: missing script delimiters')
    body = text.split('--- SCRIPT START ---',1)[1].split('--- SCRIPT END ---',1)[0]
    scene_rx = re.compile(rf'^SCENE\s+(\S+)\s*\nScene heading:\s*(.*?)\nScene start:\s*({TS})\s*\nScene end:\s*({TS})', re.M | re.I)
    block_rx = re.compile(rf'\*\*([^\n]+?)\*\*\s*\nStart:\s*\(({TS})\)\s*\|\s*End:\s*\(({TS})\)\s*\n(.*?)(?=\n\s*\*\*|\Z)', re.S)
    scenes, beats, warnings = [], [], []
    matches = list(scene_rx.finditer(body))
    for i, sm in enumerate(matches):
        scene = Scene(sm[1], sm[2], seconds(sm[3]), seconds(sm[4]))
        chunk = body[sm.end():matches[i+1].start() if i+1<len(matches) else len(body)]
        parsed = list(block_rx.finditer(chunk))
        if len(parsed) != len(re.findall(r'^\*\*',chunk,re.M)):
            raise ValueError(f'{filename}: unparsed block in scene {scene.id}')
        for bm in parsed:
            label = bm[1].rstrip(':').strip()
            kind = label if label in ('CAMERA','ACTION','SOUND FX') else 'DIALOGUE'
            b = Beat(f'{number}:{len(beats)+1}',kind,label,seconds(bm[2]),seconds(bm[3]),bm[2],bm[3],bm[4].strip(),scene.id)
            if b.end <= b.start:
                raise ValueError(f'{filename}: invalid beat bounds {b.id}')
            if b.start < scene.start or b.end > scene.end:
                warnings.append(f"{b.id}: beat extends outside declared scene; original timestamps preserved")
            beats.append(b); scene.beats.append(b)
        scenes.append(scene)
    if len(beats)!=len(re.findall(r'^\*\*',body,re.M)):
        raise ValueError(f'{filename}: source contains blocks outside recognized scenes')
    if not beats: raise ValueError(f'{filename}: no beats parsed')
    bounds = sorted({t for b in beats for t in (b.start,b.end)})
    timeline = [dict(start=a,end=z,beat_ids=[b.id for b in beats if b.start<z and b.end>a]) for a,z in zip(bounds,bounds[1:])]
    return Episode(number,filename,meta('EPISODE LOGLINE'),meta('CONTINUITY NOTES'),scenes,beats,timeline,warnings)


def parse_folder(folder):
    episodes = [parse_text(p.read_text(encoding='utf-8-sig'),p.name) for p in sorted(Path(folder).glob('*.txt'))]
    if not episodes: raise ValueError(f'No screenplay .txt files in {folder}')
    if len({e.number for e in episodes}) != len(episodes): raise ValueError('Duplicate episode numbers')
    return sorted(episodes,key=lambda e:e.number)
