import pretty_midi
import numpy as np
from midiProcessor import MIDIProcessor

midiprocessor = MIDIProcessor(1)

midiprocessor.read_all_files()

for song in midiprocessor.final_list.tolist():
    print(midiprocessor.encode_song(song))

# midiprocessor.print_final()
