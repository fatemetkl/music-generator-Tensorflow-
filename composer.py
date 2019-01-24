
import pretty_midi
import numpy as np
from midiProcessor import MIDIProcessor

midiprocessor = MIDIProcessor(1)

midiprocessor.read_all_files()
# midiprocessor.print_final()