import pretty_midi
import numpy as np
from song import Song
from sklearn.preprocessing import OneHotEncoder

class MIDIProcessor:
    
    def __init__(self, size):
        self.final_list = np.zeros((size, 1))
        self.final_list = np.empty((0, 1))
        self.size = size

    def read_all_files(self):
        for i in range(1, self.size + 1):
            song = pretty_midi.PrettyMIDI("data/{}.mid".format(i))

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
            self.final_list = np.append(self.final_list, [new_song])

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
        finalval=DurationLabel*10+VelocityLabel*100+PitchLabel
        
        return ()

    def write(self, song):
        pass

    def data_prep(self ,song):
        chars=60
        one_hot=OneHotEncoder()
        one_hot.fit(np.linspace(0,444-1,444).reshape(-1,1))
        x=one_hot.transform(np.array(self.encode_song(song)[:60])).reshape(-1,1).toarray()
        final_vector=np.zeros((60,chars))
        if(x.shape[0]>=chars):
            final_vector[:60,:chars]=x[:60,:chars]
        else:
            final_vector[:x.shape[0],:chars]=x

        return final_vector        

