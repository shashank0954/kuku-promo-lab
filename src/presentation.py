"""Code-native editorial diagrams from actual validated segment metadata."""
from html import escape

def promo_timeline_svg(item,width=1000):
    duration=item['duration'];segments=item['segments']
    left=24;usable=width-48;bar_y=54;bar_h=24
    hook_width=min(3,duration)/duration*usable
    cliff_width=min(4,duration)/duration*usable
    cursor=0
    elements=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 158" role="img" aria-label="Source promo timeline: first three seconds hook, last four seconds cliffhanger">',
              '<style>text{font-family:Arial,sans-serif;fill:#526079}.small{font-size:14px}.label{font-size:16px;font-weight:700}.time{font-family:monospace;font-size:14px}</style>',
              f'<rect width="{width}" height="158" rx="12" fill="#f6f8fc"/>',
              f'<text x="{left}" y="23" class="label" style="fill:#11805a">OPENING · FIRST 3s</text>',
              f'<text x="{width-left}" y="23" text-anchor="end" class="label" style="fill:#c83f56">CLIFFHANGER · LAST 4s</text>',
              f'<rect x="{left}" y="{bar_y}" width="{usable}" height="{bar_h}" rx="7" fill="#e0e6ee"/>',
              f'<rect x="{left}" y="{bar_y}" width="{hook_width:.2f}" height="{bar_h}" rx="7" fill="#27ae79"/>',
              f'<rect x="{left+usable-cliff_width:.2f}" y="{bar_y}" width="{cliff_width:.2f}" height="{bar_h}" rx="7" fill="#df5870"/>']
    for index,s in enumerate(segments):
        x=left+cursor/duration*usable
        if index:
            elements.extend([f'<line x1="{x:.2f}" y1="42" x2="{x:.2f}" y2="88" stroke="#14223c" stroke-width="2" stroke-dasharray="3 3"/>',
                             f'<text x="{x:.2f}" y="105" text-anchor="middle" class="small">HARD CUT</text>'])
        cursor+=s['duration']
    first=segments[0];last=segments[-1]
    elements.extend([f'<text x="{left}" y="112" class="time">E{first["episode"]} · {escape(first["start_timestamp"])}</text>',
                     f'<text x="{width-left}" y="112" text-anchor="end" class="time">E{last["episode"]} · {escape(last["end_timestamp"])}</text>',
                     f'<text x="{width/2}" y="147" text-anchor="middle" class="small">{duration:.2f}s total · {len(segments)} source segment(s) · edit boundaries preserved</text>', '</svg>'])
    return ''.join(elements)
