

    
   


    train_graph = tf.Graph()
    with train_graph.as_default():
        input_data= get_next_batch()
        lr, keep_prob = hyperparam_inputs()
        
        train_logits, inference_logits = seq2seq_model(input_data,keep_probability,batch_size,rnn_size=1024,num_layers=2)

        training_logits = tf.identity(train_logits.rnn_output, name='logits')
        inference_logits = tf.identity(inference_logits.sample_id, name='predictions')

        masks = tf.sequence_mask(target_sequence_length, max_target_sequence_length, dtype=tf.float32, name='masks')

        with tf.name_scope("optimization"):
            # Loss function - weighted softmax cross entropy
            cost = tf.contrib.seq2seq.sequence_loss(
                training_logits,
                targets,
                masks)

            # Optimizer
            optimizer = tf.train.AdamOptimizer(lr)

            # Gradient Clipping
            gradients = optimizer.compute_gradients(cost)
            capped_gradients = [(tf.clip_by_value(grad, -1., 1.), var) for grad, var in gradients if grad is not None]
            train_op = optimizer.apply_gradients(capped_gradients)



            def get_accuracy(target, logits):
        """
        Calculate accuracy
        """
        max_seq = max(target.shape[1], logits.shape[1])
        if max_seq - target.shape[1]:
            target = np.pad(
                target,
                [(0,0),(0,max_seq - target.shape[1])],
                'constant')
        if max_seq - logits.shape[1]:
            logits = np.pad(
                logits,
                [(0,0),(0,max_seq - logits.shape[1])],
                'constant')

        return np.mean(np.equal(target, logits))

    # Split data to training and validation sets
    train_source = source_int_text[batch_size:]
    train_target = target_int_text[batch_size:]
    valid_source = source_int_text[:batch_size]
    valid_target = target_int_text[:batch_size]
    (valid_sources_batch, valid_targets_batch) = next(get_batches(valid_source, valid_target,batch_size,))
                                                                                                                                                                                                            
    with tf.Session(graph=train_graph) as sess:
        sess.run(tf.global_variables_initializer())
        
        for epoch_i in range(epochs):
            
            
            for batch_i, (source_batch, target_batch) in enumerate( get_batches(train_source, train_target, batch_size])):
                   

                _, loss = sess.run(
                    [train_op, cost],
                    {input_data: source_batch,
                    targets: target_batch,
                    lr: learning_rate,
                    target_sequence_length: targets_lengths,
                    keep_prob: keep_probability})


                if batch_i % display_step == 0 and batch_i > 0:
                    batch_train_logits = sess.run(
                        inference_logits,
                        {input_data: source_batch,
                        target_sequence_length: targets_lengths,
                        keep_prob: 1.0})

                    batch_valid_logits = sess.run(
                        inference_logits,
                        {input_data: valid_sources_batch,
                        target_sequence_length: valid_targets_lengths,
                        keep_prob: 1.0})

                    train_acc = get_accuracy(target_batch, batch_train_logits)
                    valid_acc = get_accuracy(valid_targets_batch, batch_valid_logits)

                    print('Epoch {:>3} Batch {:>4}/{} - Train Accuracy: {:>6.4f}, Validation Accuracy: {:>6.4f}, Loss: {:>6.4f}'
                    .format(epoch_i, batch_i, len(source_int_text) // batch_size, train_acc, valid_acc, loss))
                        

        # Save Model
        saver = tf.train.Saver()
        saver.save(sess, save_path)
        print('Model Trained and Saved')
        
        
        def save_params(params):
            with open('params.p', 'wb') as out_file:
                pickle.dump(params, out_file)


        def load_params():
            with open('params.p', mode='rb') as in_file:
                return pickle.load(in_file)
