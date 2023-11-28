# PianAI Audio

notes
- used [VMPK](https://vmpk.sourceforge.io/) to emulate piano to generate MIDI output
- used [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) to use emulated MIDI output as input to the program (does not work internally with Windows)

libraries
- [mido](https://mido.readthedocs.io/en/stable/index.html)
- [rtmidi](https://spotlightkid.github.io/python-rtmidi/rtmidi.html#)

adapted from https://github.com/narcode/MIDI_recorder

todo
- [] compare 2 midi files, both in real time and after recording
  - (right note order, tempo, hit within threshold for timing accuracy, chords, etc)
