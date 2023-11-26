import sys
import time

from mido import MidiFile
import mido


args = sys.argv

if len(args) != 2:
    print("Usage: reader.py <.mid file to read>")
    exit()

try:
    filename = args[1]
    mid = MidiFile(f"audio/{filename}.mid")
    port = mido.open_output()

    # mid.print_tracks()
    for msg in mid.play():
        print(msg)
        port.send(msg)
    time.sleep(1)  # buffer to finish messages
except FileNotFoundError:
    print(f"File {filename}.mid not found")
