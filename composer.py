import pretty_midi 
from midiProcessor import MIDIProcessor
import numpy as np



midiprocessor = MIDIProcessor(1)

midiprocessor.read_all_files()

for song in midiprocessor.final_list.tolist():
    print(midiprocessor.data_prep(song))




# midiprocessor.print_final()
