import pretty_midi 
from midiProcessor import MIDIProcessor
import numpy as np



midiprocessor = MIDIProcessor(1)

midiprocessor.read_all_files()

for song in midiprocessor.final_list.tolist():
    l = midiprocessor.data_prep(song)
    print("SHAPE:", l.shape)
    print(l)
    # for i in l.tolist():
        # if i == 1:
            # print(i)




# midiprocessor.print_final()
