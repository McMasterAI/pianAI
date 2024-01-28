import mido
import rtmidi

from config import valid_message_types


class Recorder:
    def __init__(self, port=0, bpm=120):
        self.__port = port
        self.__bpm = bpm
        self.__time = 0

        self.__midi_in = rtmidi.MidiIn()
        self.__midi_in.open_port(port=self.__port)

        self.__midifile = mido.MidiFile()
        self.__track = mido.MidiTrack()
        self.__midifile.tracks.append(self.__track)

    def start(self) -> None:
        print("**** You are now RECORDING *****")
        print("(Press Control-C to stop the recording)\n")
        self.__midi_in.set_callback(func=self.__process_input)

    def end(self) -> None:
        self.__midi_in.close_port()

    def saveTrack(self, name: str):
        """
        Save MIDI input as a .mid file
        """
        self.__midifile.save(f"audio/{name}.mid")
        print(f"\nRecording saved as audio/{name}.mid in audio/\n")

    def __process_input(
        self, event: tuple[mido.Message, float], data: any = None
    ) -> None:
        """
        Called each time a message is received, but only processes messages
        within config.valid_message_types (e.g. note_on, note_off)
        Writes messages to the track in the MIDI file
        """
        message, deltatime = event

        if message[0] in valid_message_types:
            msg_type, msg_note, msg_velocity = message
            self.__time += deltatime

            print(message, self.__time)

            tick = self.__convert_time()

            self.__track.append(
                mido.Message(
                    type=valid_message_types[msg_type],
                    note=msg_note,
                    velocity=msg_velocity,
                    time=tick,
                )
            )

            self.__time = 0

    def __convert_time(self):
        tempo = mido.bpm2tempo(bpm=self.__bpm)
        return int(
            round(
                mido.second2tick(
                    second=self.__time,
                    ticks_per_beat=self.__midifile.ticks_per_beat,
                    tempo=tempo,
                )
            )
        )
