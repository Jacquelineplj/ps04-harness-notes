#!/usr/bin/env python3
"""Render source-labelled scene cards for import into Google Vids (requires Pillow)."""
import argparse
import re
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from heygen_render import scenes

FONT_ROOT = Path('/System/Library/Fonts/Supplemental')

def render(run_dir):
    pkg = Path(run_dir) / 'package'
    out = pkg / 'video_cards'
    out.mkdir(exist_ok=True)
    for pid in ('01', '02', '03'):
        path = pkg / f'{pid}-video-script.md'
        raw = path.read_text()
        raw_narrations = re.findall(r'^\**Narration:\** (.*)$', raw, re.M)
        for i, sc in enumerate(scenes(str(path)), 1):
            im = Image.new('RGB', (1280, 720), '#101b2c')
            d = ImageDraw.Draw(im)
            font = lambda n, bold=False: ImageFont.truetype(str(FONT_ROOT / ('Arial Bold.ttf' if bold else 'Arial.ttf')), n)
            d.rectangle((56, 54, 112, 61), fill='#55d6bc')
            d.text((56, 85), f'HARNESS NOTES  /  {pid}  /  SCENE {i:02}', font=font(22, True), fill='#55d6bc')
            title = sc.get('on_screen_text', sc['title']).strip('"')
            lines = textwrap.wrap(title, width=37)
            y = 190
            for line in lines:
                d.text((56, y), line, font=font(51, True), fill='#f5f7fb'); y += 66
            subtitle = sc['title']
            d.text((58, max(450, y+32)), subtitle[:75], font=font(28), fill='#b9c6d6')
            refs = sorted(set(re.findall(r'\[(\d+)\]', raw_narrations[i-1])), key=int)
            source = 'Source references: ' + ', '.join(f'[{n}]' for n in refs) if refs else 'Series framing and interpretation'
            d.line((56, 583, 1224, 583), fill='#37465d', width=2)
            d.text((56, 608), source, font=font(22), fill='#f5f7fb')
            d.text((56, 650), 'As of 2026-10-13  |  Sources and full article in description  |  AI-assisted presentation', font=font(20), fill='#b9c6d6')
            im.save(out / f'{pid}-{i:02}.png')
    print(out)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('run_dir'); args = ap.parse_args(); render(args.run_dir)
