class Song:
    def __init__(self, midi, max_instrument_note_length, max_vel, max_pitch, max_duration):
        self.midi = midi
        self.max_vel = max_vel
        self.max_pitch = max_pitch
        self.max_duration = max_duration
        self.max_instrument_note_length = max_instrument_note_length
