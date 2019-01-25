import math


class BatchProcessor:
    def __init__(self, data, batch_size):
        self.data = data
        self.batch_size = batch_size
        self.total_size = data
        self.max_iteration_num = math.ceil(self.total_size / batch_size)
        self.has_leftover_batch = False if self.max_iteration_num == int(self.total_size / batch_size) else True

    def get_batch(self, iteration):
        batch = []
        for item in range(iteration * self.batch_size, (iteration + 1) * self.batch_size):
            batch.append(self.data[item])

        return batch
