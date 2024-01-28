import sys
import time

from mido import MidiFile
import mido


class Reader:
    def __init__(self):
        self.port = mido.open_output()

    def open_file(self, filename: str):
        try:
            filename = f"audio/{filename}.mid"
            self.midi_file = MidiFile(filename)
        except FileNotFoundError:
            print(f"File {filename}.mid not found")

    def play(self):
        for msg in self.midi_file.play():
            print(msg)
            self.port.send(msg)
        time.sleep(1)  # buffer to finish messages


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("Usage: reader.py <.mid file to read>")
        exit()

    reader = Reader()
    reader.open_file(filename=args[1])
    reader.play()
