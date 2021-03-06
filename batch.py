import math
import midiProcessor
import numpy as np


class BatchProcessor:
    def __init__(self, batch_size, dataset_size):
        self.midi_processor = midiProcessor.MIDIProcessor(size=dataset_size)
        self.batch_size = batch_size
        self.total_size = dataset_size
        self.max_iteration_num = math.ceil(self.total_size / batch_size)
        self.has_leftover_batch = False if self.max_iteration_num == int(self.total_size / batch_size) else True
        self.batches_dict = {}
        self.last_iteration = 0

    def get_batch(self, iteration_num):
        batch = np.zeros((0, 1))
        for item in range(iteration_num * self.batch_size, (iteration_num + 1) * self.batch_size):
            if len(self.midi_processor.all_songs_objects) <= item:
                break
            else:
                batch = np.append(batch, self.midi_processor.all_songs_objects[item])
        self.batches_dict[iteration_num] = batch
        return batch

    def hot_encode_batch(self, batch):
        encoded_batch = []
        for item in batch:
            encoded_batch.append(self.midi_processor.one_hot_encode(item))

        return encoded_batch

    def print_batch(self, batch):
        for item in batch.tolist():
            print(item)

    def get_next_batch(self):
        self.midi_processor.read_files(self.last_iteration * self.batch_size,
                                       (self.last_iteration + 1) * self.batch_size)

        batch = self.get_batch(self.last_iteration)
        encoded_batch = self.hot_encode_batch(batch)

        self.last_iteration += 1
        return encoded_batch

    def reset_iterator_for_next_epoch(self):
        self.last_iteration = 0
