import pretty_midi 
from midiProcessor import MIDIProcessor
import numpy as np
import tensorflow as tf


midiprocessor = MIDIProcessor(2)

midiprocessor.read_all_files()

midiprocessor.prep_all()
