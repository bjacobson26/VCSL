#!/usr/bin/env python3
"""Import original WAVs from MechSounds and Infinite State into the B-90 repo.
No presets or redundant OP-1/Ableton copies are published. Run before build-github-sounds.py.
"""
import argparse, hashlib, importlib.util, json, re, shutil, subprocess
from pathlib import Path
spec = importlib.util.spec_from_file_location('catalog', Path(__file__).with_name('build_catalog.py'))
catalog = importlib.util.module_from_spec(spec); spec.loader.exec_module(catalog)

def classify(name, folder, collection):
    n = name.lower()
    if 'convolution' in folder.lower(): return 'FX', 'Reverb textures'
    if 'ambience' in folder.lower() or '-amb-' in n: return 'FX', 'Ambience'
    if 'sound effects' in folder.lower() or '-sfx-' in n or n.startswith('sfx-'): return 'FX', 'Effects'
    if 'percussion' in folder.lower() or '-kit-' in n or folder == 'Roland TR-8':
        if 'kick' in n or 'kik' in n: return 'Drums & Percussion', 'Kicks'
        if 'snar' in n or 'snare' in n or 'snr' in n: return 'Drums & Percussion', 'Snares'
        if 'hat' in n: return 'Drums & Percussion', 'Hi-hats'
        if 'crs' in n: return 'Drums & Percussion', 'Cymbals'
        return 'Drums & Percussion', 'Electronic percussion'
    if 'bass' in n or 'sirenbas' in n: return 'Bass', 'Synth bass'
    if 'pads and chords' in folder.lower(): return 'Pads & Chords', 'Pads'
    if 'chord' in n or 'fifth' in n: return 'Pads & Chords', 'Chords'
    if 'gameboy' in folder.lower():
        return ('FX', 'Noise') if 'noise' in n else ('Synths', 'Chiptune')
    if 'lead' in n or 'led' in n: return 'Synths', 'Leads'
    if any(x in n for x in ('pluk', 'plk', 'pluck', 'pick', 'blip')): return 'Synths', 'Plucks'
    if 'waveform' in folder.lower(): return 'Synths', 'Processed waveforms'
    return 'Synths', 'Synth tones'

def run(repo, mech, infinite, revision):
    records=[]; skipped=[]
    sources=[('MechSounds',mech/'Samples','John Oestmann','CC0-1.0','https://johnoestmannmusic.com/mechsounds/'),
             ('Infinite State',infinite/'Samples','Kenneth Reitz','LicenseRef-Infinite-State','https://kennethreitz.org/software/infinite-state-sample-pack')]
    for collection,root,creator,license,url in sources:
        for src in sorted(p for p in root.rglob('*') if p.suffix.lower() in ('.wav', '.flac')):
            relative=src.relative_to(root)
            dest=repo/'b90'/collection/relative
            if src.suffix.lower() == '.flac': dest = dest.with_name(src.stem + '-FLAC-variant.wav')
            dest.parent.mkdir(parents=True,exist_ok=True)
            if src.suffix.lower() == '.flac':
                subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-c:a','pcm_s24le',str(dest)],check=True)
            else: shutil.copy2(src,dest)
            facts=catalog.metadata(dest)
            assert facts['bytes'] <= 30_000_000, src
            family,role=classify(src.stem,relative.parts[0],collection)
            instrument=relative.parts[0] if collection=='Infinite State' else ('MechSounds · Game Boy' if 'Gameboy' in relative.parts[0] else 'MechSounds')
            instrument=instrument.replace('Monolouge','Monologue').replace('VolcaKeys','Volca Keys')
            name=src.stem
            if collection=='MechSounds':
                name=re.sub(r'^(?:010-T01-)?(?:TNL|PAD|AMB|PRC|SFX|KIT|PCW|CRT)[-_]','',name)
            name=name.replace('_',' ').replace('-',' ')
            if src.suffix.lower() == '.flac': name += ' (FLAC variant)'
            records.append(dict(id=('mech-' if collection=='MechSounds' else 'infinite-')+hashlib.sha256(relative.as_posix().encode()).hexdigest()[:24],
                name=name,kit=collection,category=role,path=dest.relative_to(repo).as_posix(),license=license,licenseUrl=url,creator=creator,
                collection=collection,family=family,instrument=instrument,articulation=role,note=None,revision=revision,isDrumKit=False,
                originalPath=relative.as_posix(),**facts))
    out=repo/'b90'
    (out/'electronic-source.json').write_text(json.dumps(records,indent=2)+'\n')
    shutil.copy2(mech/'readme.txt',out/'MechSounds'/'SOURCE-README.txt')
    (out/'Infinite State'/'LICENSE-NOTICE.md').write_text('''# Infinite State — creator permission

Creator: Kenneth Reitz. Source: https://github.com/kennethreitz/infinite-state-sample-pack
Source commit: 3964ced66fb94809f928fcdf17b9d524492f36bc
Permission: https://kennethreitz.org/software/infinite-state-sample-pack (checked 2026-10-19).

The creator describes this collection as open source and available to anyone without licensing fees or restrictions. Attribution is appreciated but not required. We retain attribution and the permission source here. This is creator permission, not a CC0 dedication; the root VCSL CC0 license does not relicense these recordings. The catalog uses LicenseRef-Infinite-State to distinguish it.

These are the original WAVs from Samples/, without modification. Redundant Ableton and OP-1 versions, presets, and drum loops are not included in this synth/sample collection.
''')
    print(json.dumps(dict(added=len(records),bytes=sum(s['bytes'] for s in records),collections=dict(__import__('collections').Counter(s['collection'] for s in records)),skipped=skipped,maxDuration=max(s['durationSeconds'] for s in records)),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('repository',type=Path);p.add_argument('--mechsounds',type=Path,required=True);p.add_argument('--infinite-state',type=Path,required=True);p.add_argument('--revision',required=True)
    a=p.parse_args();run(a.repository,a.mechsounds,a.infinite_state,a.revision)
