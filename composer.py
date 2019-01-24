
import pretty_midi
import numpy as np
from midiProcessor import MIDIProcessor

midiprocessor = MIDIProcessor(1)

midiprocessor.read_all_files()

for song in midiprocessor.final_list.tolist():
    for song_key in song.keys():
        print (midiprocessor.encode_song(song_key))
    

# midiprocessor.print_final()