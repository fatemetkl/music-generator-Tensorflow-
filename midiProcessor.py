import pretty_midi
import numpy as np


class MIDIProcessor:

    def __init__(self, size):
        self.final_list = np.zeros((size,1)) 
        self.final_list=np.empty((0,1))
        self.size = size

   

    def read_all_files(self):
        for i in range (1, self.size+1):
            song = pretty_midi.PrettyMIDI("data/{}.mid".format(i))
            # song = pretty_midi.PrettyMIDI("data/{}.mid".format(1))

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
            self.final_list = np.append(self.final_list,[{song: [maxVel, maxPitch, maxDuration]}])
            # print(self.final_list)
            # print("APPEND", i)

    def encode_song(self,song):
        encoded_song = []
        max_instrument_note_length = 0
        for instrument in song.instruments:
            if len(instrument.notes) > max_instrument_note_length:
                max_instrument_note_length = len(instrument.notes)
        for instrument in song.instruments:
            if (instrument.name == "Drum Kit 2"):
                continue
            if not instrument.is_drum:
                if len(instrument.notes) == max_instrument_note_length:  # choose the most effective instrument
                    for n in instrument.notes:
                        encoded_song.append(self.label_encoder(n,song))
                    
                            
                    break
                    

        return encoded_song

    def write(self, song):
        pass

    def label_encoder(self,note, song):
        val=self.final_list.tolist().index(song)
        d=val[2]/5
        DurationLable=(note.end-note.start)/d
        v=val[1]/5
        VelocityLable=note.velocity/v
        p=val[2]/5
        PitchLable=note.pitch/p
        return([DurationLable,VelocityLable,PitchLable])


        pass
        # binDuration=duration% np.argmax(final_list,axis=)
        # binV=n.velocity%np.argmax(final_list,axis=3)
