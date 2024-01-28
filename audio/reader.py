import sys
import time

from mido import MidiFile
import mido


class Reader:
    def __init__(self):
        self.port = mido.open_output()
        self.compare_midi_file = MidiFile(
            "audio/compare.mid"
        )  # TODO: change to arg

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

    def compare(self):
        self.__compare_notes()
        # TODO: add other analysis methods

    def __compare_notes(self):
        """
        Check that the correct notes have been played in the right order
        """

        def read_into_list(file):
            last_time = 0.0
            note_list = []
            for msg in file.play():
                curr_time = last_time + msg.time
                last_time = curr_time
                if msg.type == "note_on":
                    note_list.append((msg.note, curr_time))
            return note_list

        notes = read_into_list(self.midi_file)
        compare_notes = read_into_list(self.compare_midi_file)

        print(notes)
        print(compare_notes)
        review = []
        i, j = 0, 0
        while i < len(notes) and j < len(compare_notes):
            played = notes[i]
            compare = compare_notes[j]
            ts_diff = round(played[1] - compare[1], 4)
            comment = ["", played[0], compare[0], ts_diff]
            if abs(ts_diff) < 0.25:
                if played[0] == compare[0]:
                    comment[0] = "good!"
                else:
                    comment[0] = "wrong note"
                i += 1
                j += 1
            elif ts_diff >= 0.25:
                comment[0] = "too late / missed note"
                j += 1
            elif ts_diff <= -0.25:
                comment[0] = "too early / extra note"
                i += 1
            review.append(comment)
        while i < len(notes):
            review.append(["extra note", notes[i][0]])
            i += 1
        while j < len(compare_notes):
            review.append(["missing note", compare_notes[j][0]])
            j += 1

        print(review)


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("Usage: reader.py <.mid file to read>")
        exit()

    reader = Reader()
    reader.open_file(filename=args[1])
    # reader.play()
    reader.compare()
