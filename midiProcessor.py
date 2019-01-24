import pretty_midi
import numpy as np


class MIDIProcessor:

    def __init__(self, size):
        self.final_list = np.array(0)
        self.size = size

      

    def read_all_files(self):
        for i in (1, self.size):
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
            print([maxVel, maxPitch, maxDuration])
            np.append(self.final_list, [song, maxVel, maxPitch, maxDuration])

    def encode_song(self, song):
        midi_data = pretty_midi.PrettyMIDI(song)
        encoded_song = []
        max_instrument_note_length = 0
        for instrument in song.instruments:
            if len(instrument.notes) > max_instrument_note_length:
                max_instrument_note_length = len(instrument.notes)
        for instrument in midi_data.instruments:
            if (instrument.name == "Drum Kit 2"):
                continue
            if not instrument.is_drum:
                if len(instrument.notes) == max_instrument_note_length:  # choose the most effective instrument
                    for n in instrument.notes:
                        encoded_song.append(n)
                    break
                    

        return encoded_song

    def write(self, song):
        pass

    def label_encoder(n):
        pass
        # binDuration=duration% np.argmax(final_list,axis=)
        # binV=n.velocity%np.argmax(final_list,axis=3)
