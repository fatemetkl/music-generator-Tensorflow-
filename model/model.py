


def encoding_layer(rnn_inputs, rnn_size, num_layers, keep_prob ):


stacked_cells = tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.DropoutWrapper(tf.contrib.rnn.LSTMCell(rnn_size), keep_prob) for _ in range(num_layers)])

outputs, state = tf.nn.dynamic_rnn(stacked_cells, 
                                    embed, 
                                    dtype=tf.float32)
return outputs, state
def decoding_layer_train(encoder_state, dec_cell,output_layer, keep_prob):

    
    dec_cell = tf.contrib.rnn.DropoutWrapper(dec_cell,output_keep_prob=keep_prob) 
                                            
    
    # for only input layer
    helper = tf.contrib.seq2seq.TrainingHelper(dec_embed_input, target_sequence_length)
                                            
    
    decoder = tf.contrib.seq2seq.BasicDecoder(dec_cell, helper, encoder_state, output_layer)
                                            

    # unrolling the decoder layer
    outputs, _, _ = tf.contrib.seq2seq.dynamic_decode(decoder, impute_finished=True, maximum_iterations=max_summary_length)
                                                    
                                                    
    return outputs
                        
                        

def decoding_layer(dec_input, encoder_state,rnn_size,num_layers,batch_size, keep_prob):
        cells = tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.LSTMCell(rnn_size) for _ in range(num_layers)])

    with tf.variable_scope("decode"):
        output_layer = tf.layers.Dense(target_vocab_size)
        train_output = decoding_layer_train(encoder_state, dec_embed_input,output_layer,keep_prob)
    

    with tf.variable_scope("decode", reuse=True):
        infer_output = decoding_layer_infer(encoder_state, cells,output_layer,batch_size,keep_prob)                                               
    return (train_output, infer_output)



                            
                            




def seq2seq_model(input_data, keep_prob, batch_size,rnn_size, num_layers):
target_data=input_data
enc_outputs, enc_states = encoding_layer(input_data, rnn_size, num_layers,keep_prob)
                                        
dec_input = process_decoder_input(target_data,target_vocab_to_int, batch_size)
                    
train_output, infer_output = decoding_layer(dec_input,enc_states, rnn_size,num_layers,batch_size,keep_prob)
                                            

return train_output, infer_output





batch_size=10
display_step = 300

epochs = 13
batch_size = 128

rnn_size = 128
num_layers = 3


learning_rate = 0.001
keep_probability = 0.5