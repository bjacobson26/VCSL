----------------------------
-- MechSounds --
by John Oestmann
Last Updated 1 March 26
----------------------------

All sounds released under Public Domain / CC0
All project files released under MIT License

I have created straight WAV samples, as well as creating a .sf2 SoundFont which contains a few new instruments built from layering those WAVs.
Both of these have been used in my projects.
All of these sounds have been synthesized by me, using almost all free and open-source software.
You can explore how I synthesized these sounds under the "Samples/Project Files" folder.

The following files extensions correspond to the following software:
*.bsk - Bespoke Synth (see note on filenames below)
*.scd - SuperCollider
*.vcv - VCV Rack
*.fxp - Surge XT
*.xml - SocaLabs Wavetable
*.vital - Vitalium (should work with Vital)
*.txt - Floral Sample Toolkit
*.sf2 - SoundFont

If a project file has words after the sample name, the next word is the name of a VST or other plugin that was used. For example, "TNL-WOODPLUK-RipplerX.bsk" requires the RipplerX VST3 plugin to be available in Bespoke Synth to load the project file properly. This is usually due to certain plugins not allowing presets to be saved in their own DAW-agnostic format, or if I've used multiple VSTs in a chain. Note that it may be the LV2 versions in the case of some plugins, so if the VST3 version isn't loading automatically in Bespoke Synth, try installing and scanning for the LV2 version too.

I created the SoundFont with the open-source program Polyphone. You can also explore the inner workings of this SoundFont using Polyphone.

-------------
SoundFont Banks / Sample Categories:
-------------
MULTI-LAYERED (Made up of several of the WAV samples)
000 - TNL - Tonal
001 - PAD - Tonal Ambient Pad, often a long and complex chord.
002 - AMB - Non-tonal SFX Ambience Pad
003 - PRC - Single Percussion
004 - SFX - Sound Effect
005 - KIT - A kit of sounds, where each key is a different sound

SINGLE-LAYERED (Direct implementation of each WAV sample)
010 - TNL - Tonal
011 - PAD - Tonal Ambient Pad, often a long and complex chord.
012 - AMB - Non-tonal SFX Ambience Pad
013 - PRC - Single Percussion
014 - SFX - Sound Effect
015 - PCW - Classic waveforms (Square, Tri, etc) with Effects Processing 

MISC:
101 - a_new_day_in_the_workshop extracted sounds (from tracks created before this Sound Pack was planned)
102 - Gameboy Waveforms drawn and saved from Furnace Tracker
103 - Convolution Reverb Textures - Synthesized textures to use as Impulse Responses in Convolution Reverbs

--------------
Extra Notes
--------------
The sounds in Samples folder "102 - Furnace Gameboy" are recordings from Furnace tracker's Gameboy emulation. I haven't included project files, as they are generated mostly using the Gameboy defaults in Furnace, and some simple drawn waves.
You can download the open-source Furnace tracker from https://tildearrow.org/furnace/

