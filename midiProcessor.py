import pretty_midi
import numpy as np
from song import Song
from sklearn.preprocessing import OneHotEncoder
# import tensorflow as tf


class MIDIProcessor:

    def __init__(self, size):
        self.all_songs_objects = np.zeros((size, 1))
        self.all_songs_objects = np.empty((0, 1))
        self.size = size
        self.one_hot_encoder = OneHotEncoder(categories='auto')
        self.one_hot_encoder.fit(np.linspace(0, 443, 444).reshape(-1, 1))
        self.final_network_input = np.zeros((size, 1))
        self.final_network_input = np.empty((0, 1))

    def read_files(self, start_file, end_file):
        print("start = ", start_file, "end =", end_file)
        for i in range(start_file+1, end_file):
            try:
                song = pretty_midi.PrettyMIDI("data/{}.mid".format(i))
            except:
                break

            maxVel, maxPitch, maxDuration = 0.0, 0.0, 0.0
            max_instrument_note_length = 0
            for instrument in song.instruments:
                if len(instrument.notes) > max_instrument_note_length:
                    max_instrument_note_length = len(instrument.notes)
            for instrument in song.instruments:
                if len(instrument.notes) == max_instrument_note_length:
                    maxVel, maxPitch, maxDuration = 0.0, 0.0, 0.0
                    for note in instrument.notes:
                        duration = note.end - note.start
                        if (duration > maxDuration):
                            maxDuration = duration
                        if (note.velocity > maxVel):
                            maxVel = note.velocity
                        if (note.pitch > maxPitch):
                            maxPitch = note.pitch
                    break

            new_song = Song(song, max_instrument_note_length, maxVel, maxPitch, maxDuration)
            print(new_song.max_vel)
            self.all_songs_objects = np.append(self.all_songs_objects, [new_song])

    def one_hot_encode(self, song):
        indices = self.encode_song(song)[:60]
        depth = 444
        x = tf.one_hot(indices, depth)
        return x

    def encode_song(self, song):
        encoded_song = []
        max_instrument_note_length = 0
        for instrument in song.midi.instruments:
            if len(instrument.notes) > max_instrument_note_length:
                max_instrument_note_length = len(instrument.notes)
        for instrument in song.midi.instruments:
            if (instrument.name == "Drum Kit 2"):
                continue
            if not instrument.is_drum:
                if len(instrument.notes) == max_instrument_note_length:  # choose the most effective instrument
                    for n in instrument.notes:
                        encoded_song.append(self.label_encoder(n, song))
                    break
        return encoded_song

    # TODO: Check SONG OR ALL?
    def label_encoder(self, note, song):
        d = song.max_duration / 5
        DurationLabel = int((note.end - note.start) % d)
        v = song.max_vel / 5
        VelocityLabel = int(note.velocity % v)
        p = song.max_pitch / 5
        PitchLabel = int(note.pitch % p)
        return DurationLabel * 10 + VelocityLabel * 100 + PitchLabel

    def write(self, song):
        pass
