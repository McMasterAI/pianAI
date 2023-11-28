import time

from recorder import Recorder


try:
    recorder = Recorder()
    recorder.start()
except Exception as e:
    print("Error encountered when starting recorder:")
    print(e)
    exit()

try:
    while True:
        time.sleep(0.001)
except KeyboardInterrupt:
    print("")
finally:
    name = input(
        "\nSave MIDI recording as? (leaving the name blank discards the \
            recording): "
    )
    if name != "":
        recorder.saveTrack(name)
recorder.end()
