# PianAI Audio


### Setup
1. Install the emulation software if needed (see below)
2. Install requirements (instructions for Windows are the following)
```python
cd audio
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### Emulation software
- used [VMPK](https://vmpk.sourceforge.io/) to emulate piano to generate MIDI output
- used [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) to use emulated MIDI output as input to the program (does not work without external tooling with Windows)

#### Libraries
- [mido](https://mido.readthedocs.io/en/stable/index.html)
- [rtmidi](https://spotlightkid.github.io/python-rtmidi/rtmidi.html#)

### Usage

- To record: `python main.py`
- To read a `.mid` file: `python reader.py <name of file without .mid extention (e.g. file1)>`


### Notes
- Adapted from https://github.com/narcode/MIDI_recorder

### Todo

- [ ] compare 2 midi files, both in real time and after recording for analysis
  - (right note order, tempo, hit within threshold for timing accuracy, chords, etc)
