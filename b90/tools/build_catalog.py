#!/usr/bin/env python3
"""Build the B-90 catalog from the complete VCSL tree and migrated Holizna packs.
Requires Python 3 and ffmpeg (only for the 24 MP3/OGG source samples).
Audio stays unchanged except for lossless decoding of those compressed sources.
"""
import argparse, collections, hashlib, json, re, shutil, struct, subprocess
from pathlib import Path

ROOTS = ('Aerophones', 'Chordophones', 'Electrophones', 'Idiophones', 'Membranophones')
STYLES = {'Sus': 'Sustain', 'Sustains': 'Sustain', 'SusVib': 'Sustain with vibrato',
          'Vib': 'Vibrato', 'HandVib': 'Hand vibrato', 'Stac': 'Staccato',
          'Rel': 'Release', 'Releases': 'Release', 'NoSus': 'Without sustain pedal',
          'LongBow': 'Long bow', 'Pluck': 'Plucked', 'Gliss': 'Glissando',
          'stop1': 'Stop 1', 'Non-Vibrato': 'Without vibrato'}

def natural(value):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)', value)]

def metadata(path):
    data = path.read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WAVE', path
    offset = 12; size = rate = align = channels = None
    while offset + 8 <= len(data):
        kind, length = struct.unpack_from('<4sI', data, offset); offset += 8
        if kind == b'fmt ':
            _, channels, rate, _, align = struct.unpack_from('<HHIIH', data, offset)
        if kind == b'data': size = length
        offset += length + length % 2
    assert size and rate and align, path
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                durationSeconds=round(size / align / rate, 6), sampleRate=rate, channels=channels)

def family(parts):
    root, instrument = parts[0], parts[2]
    lower = instrument.lower()
    if root == 'Electrophones': return 'Synths'
    if 'piano' in lower or 'harpsichord' in lower: return 'Pianos & Keys'
    if 'organ' in lower: return 'Organs'
    if root == 'Chordophones': return 'Strings & Plucked'
    if root == 'Aerophones':
        if 'Siren' in instrument or 'Whistle' in instrument: return 'Whistles & FX'
        return 'Woodwinds & Reeds'
    if root == 'Membranophones': return 'Drums & Percussion'
    if any(x in lower for x in ['marimba', 'glockenspiel', 'xylophone', 'vibraphone', 'balafon', 'kalimba', 'mbira', 'nyunga', 'wine glasses', 'tubular bells', 'hand chimes']): return 'Mallets & Tuned Percussion'
    return 'Drums & Percussion'

def build(repo, revision, holizna):
    out = repo / 'b90'; out.mkdir(exist_ok=True)
    if holizna:
        source = json.loads((holizna / 'catalog.json').read_text())
        migrated = []
        for sound in source['samples']:
            old = holizna / sound['path']; facts = metadata(old)
            assert facts['bytes'] == sound['bytes'] and facts['sha256'] == sound['sha256'], old
            destination = out / 'Holizna' / sound['kit'] / sound['category'] / old.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old, destination)
            sound['path'] = destination.relative_to(repo).as_posix()
            sound.pop('previewPath', None)
            sound.update(collection='Holizna Drum Kits', instrument=sound['kit'], articulation=sound['category'], isDrumKit=True)
            migrated.append(sound)
        (out / 'holizna-source.json').write_text(json.dumps(migrated, indent=2) + '\n')
        shutil.copy2(holizna / 'CREDITS.txt', out / 'HOLIZNA-CREDITS.txt')
    samples = json.loads((out / 'holizna-source.json').read_text())
    for sound in samples:
        sound['revision'] = revision
        facts = metadata(repo / sound['path'])
        assert facts['sha256'] == sound['sha256']
    originals = sorted([p for root in ROOTS for p in (repo / root).rglob('*') if p.suffix.lower() in ('.wav', '.ogg', '.mp3')])
    for original in originals:
        relative = original.relative_to(repo); parts = relative.parts
        instrument = parts[2] if parts[0] != 'Electrophones' else 'TX81Z · ' + parts[2]
        style = ' / '.join(STYLES.get(x, x) for x in parts[3:-1]) or 'One-shot'
        note = re.search(r'(?:^|[_\s-])([A-G](?:#|b)?-?\d)(?=[_\s.-]|$)', original.stem)
        audio = original
        if original.suffix.lower() != '.wav':
            audio = out / 'Converted' / relative.with_suffix('.wav')
            audio.parent.mkdir(parents=True, exist_ok=True)
            if not audio.exists():
                subprocess.run(['ffmpeg', '-v', 'error', '-i', str(original), '-c:a', 'pcm_s24le', str(audio)], check=True)
        facts = metadata(audio)
        # Retain original filenames (including velocity/round-robin markers) to distinguish every recording.
        samples.append(dict(id='vcsl-' + hashlib.sha256(relative.as_posix().encode()).hexdigest()[:24],
            name=original.stem.replace('_', ' '), kit='VCSL', category=style,
            path=audio.relative_to(repo).as_posix(), license='CC0-1.0', creator='Versilian Studios and VCSL contributors',
            collection='VCSL', family=family(parts), instrument=instrument, articulation=style,
            note=note.group(1) if note else None, revision=revision, isDrumKit=False,
            originalPath=relative.as_posix(), **facts))
    samples.sort(key=lambda s: (natural(s.get('family', 'Drums & Percussion')), natural(s['instrument']), natural(s['articulation']), natural(s['name']), s['id']))
    assert len({s['id'] for s in samples}) == len(samples)
    assert all(s['bytes'] <= 30_000_000 and s['durationSeconds'] > 0 for s in samples)
    catalog = dict(schemaVersion=2, title='B-90 Open Sound Library', repository='https://github.com/bjacobson26/VCSL',
        licenseUrl='https://creativecommons.org/publicdomain/zero/1.0/', samples=samples)
    (out / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')) + '\n')
    stats = dict(samples=len(samples), vcslSamples=len(originals), holiznaSamples=len(samples)-len(originals),
                 bytes=sum(s['bytes'] for s in samples), families=dict(collections.Counter(s.get('family','Drums & Percussion') for s in samples)),
                 instruments=len({s['instrument'] for s in samples}), revision=revision)
    (out / 'inventory.json').write_text(json.dumps(stats, indent=2) + '\n')
    print(json.dumps(stats, indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('--revision', required=True, help='Immutable Git tag to publish after this catalog is committed')
    parser.add_argument('--holizna', type=Path, help='Existing exported Cloudflare catalog and original WAVs; needed only for initial migration')
    args=parser.parse_args(); build(args.repository.resolve(), args.revision, args.holizna)
