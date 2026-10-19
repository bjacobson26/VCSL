# B-90 Open Sound Library

A freely downloadable collection of sounds for B-90 and other samplers. No account or API key is required. The original VCSL collection is preserved in its existing folders; this directory adds an indexed catalog and the Holizna drum packs previously hosted on Cloudflare.

## Collections and licensing

- **VCSL:** the complete audio collection in this fork, by Versilian Studios and its contributors. See the repository's original README and CC0 `LICENSE`. Source folders and supporting recording notes are preserved. Every WAV is cataloged, including alternate takes, velocity layers, releases, and legacy instruments. The 18 OGG and six MP3 recordings also appear in the catalog as decoded WAVs in `Converted/`; their original compressed files remain in place.
- **Holizna Drum Kits:** all 407 original sounds across nine packs. See `HOLIZNA-CREDITS.txt` for the source and CC0 dedication. The original audio and B-90 sample IDs are preserved.

All cataloged audio is CC0-1.0. This permits reuse, modification, and redistribution, including in commercial projects. Source credits remain in the catalog as a courtesy. No artwork is added from the Holizna packs. Catalog tooling in `tools/` is also contributed under the repository's CC0 dedication.

## Browse and download

`catalog.json` is the machine-readable index. It contains family, instrument/pack, playing style, note (when explicitly identifiable in the filename), source credit, original source path, duration, size, SHA-256, and a pinned Git revision. Filename details such as velocity and round-robin remain visible so recordings can be distinguished.

Families use everyday names: Pianos & Keys, Organs, Synths, Strings & Plucked, Woodwinds & Reeds, Mallets & Tuned Percussion, Whistles & FX, and Drums & Percussion. Instruments use the original collection folder names. Playing styles come from articulation subfolders. No samples are ranked or curated out.

B-90 reads the current catalog from:

https://raw.githubusercontent.com/bjacobson26/VCSL/master/b90/catalog.json

Audio is fetched using the catalog's pinned `revision` and repository-relative `path` (URL-encode special characters). For example, prepend `https://raw.githubusercontent.com/bjacobson26/VCSL/<revision>/` to the encoded path. Do not use GitHub's HTML `blob` page as an audio URL. No GitHub API calls or access tokens are needed by clients.

B-90 downloads audio only when previewing or saving. A temporary preview cache avoids repeat downloads; saved sounds remain available offline. The full collection is not bundled in the app. Kits are the existing balanced Holizna drum selections; individual instrument collections are not automatically turned into drum kits.

## Rebuild the catalog

Requires Python 3 and ffmpeg for the OGG/MP3 conversions. From the repository root:

```
python3 b90/tools/build_catalog.py . --revision b90-library-v2
```

Commit the resulting catalog and any new audio, then create and push the matching immutable tag before clients fetch the new catalog. Never move an existing published tag. Verify the sizes and checksums and keep IDs stable when editing metadata. `inventory.json` summarizes the resulting collection. `holizna-source.json` preserves the migrated source metadata for rebuilding.

GitHub hosting is subject to GitHub's terms and availability; this project does not promise unlimited or permanent free hosting.
