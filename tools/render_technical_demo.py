#!/usr/bin/env python3
"""Create an explicitly AI-narrated walkthrough of real saved repository artifacts.
macOS: requires say, Pillow, and PyAV. Output media stays in demo/rendered/.
"""
from pathlib import Path
from fractions import Fraction
import json, math, re, subprocess
import av
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'demo/rendered'
FIRST = ROOT/'runs/20261013T213636Z-podcasts-expanded'
SECOND = ROOT/'runs/20261014T014037Z-second-live'

def load(p): return json.loads(p.read_text())
def wrap(draw,text,font,width):
    lines=[]
    for paragraph in text.splitlines():
        line=''
        for word in paragraph.split():
            test=(line+' '+word).strip()
            if draw.textlength(test,font=font)>width and line: lines.append(line);line=word
            else:line=test
        lines.append(line)
    return lines

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    summary=load(SECOND/'summary.json')
    script=(ROOT/'demo/technical_demo_script.md').read_text()
    parts=re.findall(r'## ([^\n]+)\n(.*?)(?=\n## |\Z)',script,re.S)
    narrations=[]
    for heading,body in parts:
        match=re.search(r'“(.*?)”\s*$',body,re.S)
        if match:narrations.append((heading,' '.join(match.group(1).split())))
    assert len(narrations)==7,len(narrations)
    narrations[3]=(narrations[3][0], 'The first final live run uses October 13 UTC. The second uses October 14 UTC, although both started on October 13 in New York. These are different UTC execution dates, not a claim of twenty-four hours between runs. The second run discovered 74 candidates and extracted 67 items. All 67 were unchanged in the persistent store; no new or changed versions were found. All 25 media transcripts were reused. Intervening runs had already expanded the eligible corpus to 73 items. With policy version two, selection accepted 27, rejected 45, and deferred one. The new briefs cite three podcasts rather than one. Content checks pass, but human editorial approval is still pending. The labelled injected replay is an update demonstration, not a substitute for live collection.')
    cards=[
      ('Harness Notes','An inspectable intelligence pipeline','run.sh\n  config + prompt snapshots\n  collect_sources.sh\n    feeds / YouTube / podcasts\n    extraction -> evidence store -> date filter\n  create_series.sh\n    decisions -> briefs -> articles + scripts\n    content checks -> human approval -> package','SUBMISSION.md / Architecture'),
      ('Stage contracts','Streams, snapshots, receipts','Input/output: JSON Lines\nEvidence: immutable item + version references\nWindow: 30 publication dates ending at run date\nReceipt: status, counts, errors, time, cost\nApproval: review_id must match current inputs\nPublishing: separate from generation','run.sh; workflows/collect_sources.sh; workflows/create_series.sh'),
      ('Trace claim 03-c9','A claim needs two retained passages','MLOps Community / published 2026-09-28\nAWS Has 16,000 APIs. Can MCP Handle It?\n\nDecision: accept -> pieces 01 / 02 / 03\nVersion: 72917d775f28...\ns-0068  30:48-31:17  ~16,000 AWS APIs\ns-0034  15:01-15:29  generated Python hard to review\n\nBrief -> article 03 -> script 03 -> public Substack','tools/trace_claim.sh ... 03-c9; package/03-sources.md'),
      ('Second live run','Measured repeat-run results',f"UTC date: {summary['as_of_date']}\nNew: 0    Changed: 0    Unchanged: 67\nEligible: 73    Accepted: 27    Rejected: 45    Deferred: 1\nMedia transcripts reused: 25 / 25\nOutputs: 3 briefs + 3 articles + 3 scripts\nContent checks: pass / 0 errors / 5 warnings\nStatus: awaiting human editorial review\n\nBoth live runs started Oct 13 in New York.",'runs/20261014T014037Z-second-live/summary.json'),
      ('Failure remains visible','A stored corpus is not current collection coverage','Label: simulated-failure\nSIMULATE_COLLECTOR_FAILURE=podcasts\n\nfeeds: exit 0     YouTube: exit 0\npodcasts: exit 1  simulated: true\n\ncoverage_complete: false\nUsable results preserved; failure recorded.\nStopped after collection, not a publication run.','runs/20261014T005920Z-simulated-failure/summary.json'),
      ('Editorial intervention','Attribution and policy changes','Correction before first approval:\n  Martin Fowler -> Naresh Jain\n  Website host is not the author.\n\nPolicy-v2 replay: same evidence\n  27 / 33 / 7 -> 30 / 36 / 1\n  52 identical decisions; 15 changed\n  Includes piece-assignment changes.','corrections.jsonl; policy-v2/decisions_diff.md'),
      ('Storage and handoff','The database alone is not the archive','SQLite index + content-addressed asset files\n\nBenefits: compact index; inspectable evidence\nTradeoff: index and assets must travel together\n\nPackage: articles, scene scripts, sources, descriptions\nSubstack: three public articles verified without login\nVideo rendering and upload are separate operations.','data/store.py; package/manifest.json')]
    metadata=[];audio_frames=[];boundaries=[];samples=0
    fontroot=Path('/System/Library/Fonts/Supplemental')
    for i,((heading,narration),card) in enumerate(zip(narrations,cards),1):
        textfile=OUT/f'{i:02}.txt';textfile.write_text(narration)
        audiofile=OUT/f'{i:02}.aiff'
        subprocess.run(['say','-v','Samantha','-r','158','-f',str(textfile),'-o',str(audiofile)],check=True)
        resampler=av.AudioResampler(format='fltp',layout='mono',rate=48000)
        start=samples
        with av.open(str(audiofile)) as source:
            for frame in source.decode(audio=0):
                for converted in resampler.resample(frame):
                    converted.pts=samples;converted.time_base=Fraction(1,48000);samples+=converted.samples;audio_frames.append(converted)
            for converted in resampler.resample(None):
                converted.pts=samples;converted.time_base=Fraction(1,48000);samples+=converted.samples;audio_frames.append(converted)
        boundaries.append(samples/48000)
        im=Image.new('RGB',(1920,1080),'#101b2c');d=ImageDraw.Draw(im)
        title,subtitle,body,source=card
        font=lambda size,bold=False:ImageFont.truetype(str(fontroot/('Arial Bold.ttf' if bold else 'Arial.ttf')),size)
        d.text((80,55),f'HARNESS NOTES / TECHNICAL WALKTHROUGH / {i:02}',font=font(27,True),fill='#55d6bc')
        d.text((80,120),title,font=font(62,True),fill='#f5f7fb')
        d.text((80,209),subtitle,font=font(34),fill='#b9c6d6')
        y=305
        mono=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',31)
        for line in wrap(d,body,mono,1750):
            d.text((80,y),line,font=mono,fill='#f5f7fb');y+=49
        assert y<940,(i,y)
        d.line((80,944,1840,944),fill='#37465d',width=2)
        d.text((80,971),source,font=font(25),fill='#b9c6d6')
        d.text((80,1020),'AI-narrated walkthrough of saved artifacts | Rendered evidence cards; not a live screen recording',font=font(23),fill='#55d6bc')
        im.save(OUT/f'{i:02}.png')
        metadata.append({'scene':i,'heading':heading,'narration':narration,'duration_seconds':(samples-start)/48000,'source':source})
    duration=samples/48000
    assert 240<=duration<=360,duration
    with av.open(str(OUT/'technical-demo.mp4'),'w') as dest:
        video=dest.add_stream('libx264',rate=2);video.width=1920;video.height=1080;video.pix_fmt='yuv420p';video.options={'crf':'22','preset':'veryfast'}
        audio=dest.add_stream('aac',rate=48000);audio.layout='mono';audio.bit_rate=128000
        images=[Image.open(OUT/f'{i:02}.png') for i in range(1,8)]
        for n in range(math.ceil(duration*2)):
            idx=next((j for j,t in enumerate(boundaries) if n/2<t),6)
            frame=av.VideoFrame.from_image(images[idx]);frame.pts=n
            for packet in video.encode(frame):dest.mux(packet)
        for packet in video.encode():dest.mux(packet)
        for frame in audio_frames:
            for packet in audio.encode(frame):dest.mux(packet)
        for packet in audio.encode():dest.mux(packet)
    (ROOT/'demo/technical_demo_manifest.json').write_text(json.dumps({'duration_seconds':duration,'presentation':'AI-narrated rendered evidence walkthrough, not a live screen recording','scenes':metadata},indent=2)+'\n')
    print(f'{OUT}/technical-demo.mp4 ({duration:.1f} seconds)')

if __name__=='__main__':main()
