
import pretty_midi 
import numpy as np



for i in (1,1):

    song=pretty_midi.PrettyMIDI("data/{}.mid".format(i))
    
    max_instrument_note_length = 0
    for instrument in song.instruments:
        if len(instrument.notes)>max_instrument_note_length:
            max_instrument_note_length = len(instrument.notes)
    for instrument in song.instrument:
        if len(instrument.notes)==max_instrument_note_length:
            maxVel=0.0
            maxPitch=0.0
            maxDuration=0.0   
            for note in instrument.notes:
                    duration=note.end - note.start
                    if(duration>maxDuration):
                        maxDuration=duration
                    if(note.velocity>maxVel):
                        maxVel=note.velocity
                    if(note.pitch>maxPitch):
                        maxPitch=note.pitch        
            break


    final_list.append([song,maxVel,maxPitch,maxDuration])