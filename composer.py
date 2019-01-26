from batch import BatchProcessor


batch_processor = BatchProcessor(batch_size=20, dataset_size=2)

for iteration in range(0, batch_processor.max_iteration_num):
    print("ITERATION =", iteration)
    batch_processor.midi_processor.read_files(iteration * batch_processor.batch_size,
                              (iteration + 1) * batch_processor.batch_size)

    batch = batch_processor.get_batch(iteration)
    # encoded_batch = batch_processor.hot_encode_batch(batch)
