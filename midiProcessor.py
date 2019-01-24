import pretty_midi 
import numpy as np

final_list=np.array(1,4)

# def lable_encoder(n):
    
#     binDuration=duration% np.argmax(final_list,axis=)
#     binV=n.velocity%np.argmax(final_list,axis=3)
    
    





def encode_song(song):
    midi_data=pretty_midi.PrettyMIDI(song)
    encoded_song=[]
    max_instrument_note_length = 0
    for instrument in song.instruments:
        if len(instrument.notes)>max_instrument_note_length:
            max_instrument_note_length = len(instrument.notes)
    for instrument in midi_data.instruments:
        if(instrument.name=="Drum Kit 2"):
            continue
        if not instrument.is_drum:
            if len(instrument.notes)==max_instrument_note_length :  #choose the most effective instrument
                for n in instrument.notes:
                    encoded_song.append(n)
                break


    return encoded_song            




                  


