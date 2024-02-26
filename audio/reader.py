import sys
import time

from mido import MidiFile
import mido

import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.layouts import row
from bokeh.plotting import figure

class Reader:
    def __init__(self):
        self.port = mido.open_output()
        self.compare_midi_file = MidiFile(
            "audio/ref3.mid"
        )  # TODO: change to arg
        self.review = []

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
            self.review.append(comment)
        while i < len(notes):
            self.review.append(["extra note", notes[i][0]])
            i += 1
        while j < len(compare_notes):
            self.review.append(["missing note", compare_notes[j][0]])
            j += 1

        print(self.review)

    def plot(self):

        def create_data(self, file):
            last_time = 0.0

            #List
            list_freq = []
            list_start_time = []
            list_end_time = []

            for msg in file.play():
                
                #Calculating time of message
                curr_time = last_time + msg.time
                last_time = curr_time

                if msg.type == "note_on":
                    list_freq.append(msg.note)
                    list_start_time.append(curr_time)
                else:
                    list_end_time.append(curr_time)
            
            #Combine lists into 1 dataframe
            list_of_tuples = list(zip(list_freq, list_start_time, list_end_time))
            df = pd.DataFrame(list_of_tuples, columns=["Frequency", "Start_time", "End_time"])

            return df

        #Creating dataframes for both sets of data
        played_notes_df = create_data(self, self.midi_file)
        reference_notes_df = create_data(self, self.compare_midi_file)

        output_file("plot.html")
        
        #Convert dataframes to columnDataSource to be used in Bokeh library
        played_notes_source = ColumnDataSource(played_notes_df)
        reference_notes_source = ColumnDataSource(reference_notes_df)


        combined_notes_plot = figure(width=1000, height=1000, toolbar_location=None, title="Midi pitch of both set of notes")
        #Adding played notes
        combined_notes_plot.hbar(y="Frequency", left="Start_time", right="End_time", height=0.4, legend_label="Played notes", fill_color="red", source=played_notes_source)
        #Adding reference notes
        combined_notes_plot.hbar(y="Frequency", left="Start_time", right="End_time", height=0.4, legend_label="Reference notes", fill_color="blue", source=reference_notes_source)

        #Plot legend settings
        combined_notes_plot.legend.location = "top_left"
        combined_notes_plot.legend.click_policy="mute"
        #Axis titles
        combined_notes_plot.xaxis.axis_label = "Time (seconds)"
        combined_notes_plot.yaxis.axis_label = "Pitch (MIDI)"


        show(combined_notes_plot)

    def final_report(self):
        
        count=1

        for list in self.review:
            #Store HTML file contents as a string
            with open("plot.html", "r") as html_file:
                existing_content = html_file.read()

            if list[0] == "good!":
                new_content = f"""
    <div>
        <h2>Note #{count}</h2>
        <p>Good!</p>
    </div>
"""
            elif list[0] == "wrong note":
                pitch_difference = list[2]-list[1]
                new_content = f"""
    <div>
        <h2>Note #{count}</h2>
        <p>
        Wrong note played.
        Pitch is off by {pitch_difference}
        </p>
    </div>
"""                
            elif list[0] == "too late/missed note":
                new_content = f"""
    <div>
        <h2>Note #{count}</h2>
        <p>
        Too late/missed note
        Note was played {list[3]} after original note
        </p>
    </div>
"""                

            elif list[0] == "extra note":
                new_content = f"""
    <div>
        <h2>Note #{count}</h2>
        <p>
        Extra note played
        </p>
    </div>
"""                

            elif list[0] == "missing note":
                new_content = f"""
    <div>
        <h2>Note #{count}</h2>
        <p>
        Missing Note!
        </p>
    </div>
"""                
            count+=1
            
            #Rewrite HTML with note message
            modified_content = existing_content.replace("</body>", f"{new_content}\n</body>",1)
        
            #Store modified file back to HTML file
            with open("plot.html", "w") as html_file:
                html_file.write(modified_content)

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("Usage: reader.py <.mid file to read>")
        exit()

    reader = Reader()
    reader.open_file(filename=args[1])
    # reader.play()
    reader.compare()
    reader.plot()
    reader.final_report()