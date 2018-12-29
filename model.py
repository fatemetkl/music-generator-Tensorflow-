

"""
Model to generate new songs

"""

import numpy as np  # To generate random numbers
import tensorflow as tf

from deepmusic.moduleloader import ModuleLoader
from deepmusic.keyboardcell import KeyboardCell
import deepmusic.songstruct as music


class Model:
    """
    Base class which manage the different models and experimentation.
    """

    class TargetWeightsPolicy:
        """ Structure to represent the different policy for choosing the target weights
        This is used to scale the contribution of each timestep to the global loss
        """
        NONE = 'none'  # All weights equals (=1.0) (default behavior)
        LINEAR = 'linear'  # The first outputs are less penalized than the last ones
        STEP = 'step'  # We start penalizing only after x steps (enco/deco behavior)

        def __init__(self, args):
            """
            Args:
                args: parameters of the model
            """
            self.args = args

        def get_weight(self, i):
            """ Return the target weight for the given step i using the chosen policy
            """
            if not self.args.target_weights or self.args.target_weights == Model.TargetWeightsPolicy.NONE:
                return 1.0
            elif self.args.target_weights == Model.TargetWeightsPolicy.LINEAR:
                return i / (self.args.sample_length - 1)  # Gradually increment the loss weight
            elif self.args.target_weights == Model.TargetWeightsPolicy.STEP:
                raise NotImplementedError('Step target weight policy not implemented yet, please consider another policy')
            else:
                raise ValueError('Unknown chosen target weight policy: {}'.format(self.args.target_weights))

        @staticmethod
        def get_policies():
            """ Return the list of the different modes
            Useful when parsing the command lines arguments
            """
            return [
                Model.TargetWeightsPolicy.NONE,
                Model.TargetWeightsPolicy.LINEAR,
                Model.TargetWeightsPolicy.STEP
            ]

    class ScheduledSamplingPolicy:
        """ Container for the schedule sampling policy
        See http://arxiv.org/abs/1506.03099 for more details
        """
        NONE = 'none'  # No scheduled sampling (always take the given input)
        ALWAYS = 'always'  # Always samples from the predicted output
        LINEAR = 'linear'  # Gradually increase the sampling rate

        def __init__(self, args):
            self.sampling_policy_fct = None

            assert args.scheduled_sampling
            assert len(args.scheduled_sampling) > 0

            policy = args.scheduled_sampling[0]
            if policy == Model.ScheduledSamplingPolicy.NONE:
                self.sampling_policy_fct = lambda step: 1.0
            elif policy == Model.ScheduledSamplingPolicy.ALWAYS:
                self.sampling_policy_fct = lambda step: 0.0
            elif policy == Model.ScheduledSamplingPolicy.LINEAR:
                if len(args.scheduled_sampling) != 5:
                    raise ValueError('Not the right arguments for the sampling linear policy ({} instead of 4)'.format(len(args.scheduled_sampling)-1))

                start_step = int(args.scheduled_sampling[1])
                end_step = int(args.scheduled_sampling[2])
                start_value = float(args.scheduled_sampling[3])
                end_value = float(args.scheduled_sampling[4])

                if (start_step >= end_step or
                   not (0.0 <= start_value <= 1.0) or
                   not (0.0 <= end_value <= 1.0)):
                    raise ValueError('Some schedule sampling parameters incorrect.')

                # TODO: Add default values (as optional arguments)

                def linear_policy(step):
                    if step < start_step:
                        threshold = start_value
                    elif start_step <= step < end_step:
                        slope = (start_value-end_value)/(start_step-end_step)  # < 0 (because end_step>start_step and start_value>end_value)
                        threshold = slope*(step-start_step) + start_value
                    elif end_step <= step:
                        threshold = end_value
                    else:
                        raise RuntimeError('Invalid value for the sampling policy')  # Parameters have not been correctly defined!
                    assert 0.0 <= threshold <= 1.0
                    return threshold

                self.sampling_policy_fct = linear_policy
            else:
                raise ValueError('Unknown chosen schedule sampling policy: {}'.format(policy))

        def get_prev_threshold(self, glob_step, i=0):
            """ Return the previous sampling probability for the current step.
            If above, the RNN should use the previous step instead of the given input.
            Args:
                glob_step (int): the global iteration step for the training
                i (int): the timestep of the RNN (TODO: implement incrementive slope (progression like -\|), remove the '=0')
            """
            return self.sampling_policy_fct(glob_step)

    def __init__(self, args):
        """
        Args:
            args: parameters of the model
        """
        print('Model creation...')

        self.args = args  # Keep track of the parameters of the model

        # Placeholders
        self.inputs = None
        self.targets = None
        self.use_prev = None  # Boolean tensor which say at Graph evaluation time if we use the input placeholder or the previous output.
        self.current_learning_rate = None  # Allow to have a dynamic learning rate

        # Main operators
        self.opt_op = None  # Optimizer
        self.outputs = None  # Outputs of the network
        self.final_state = None  # When testing, we feed this value as initial state ?

        # Other options
        self.target_weights_policy = None
        self.schedule_policy = None
        self.learning_rate_policy = None
        self.loop_processing = None

        # Construct the graphs
        self._build_network()

    def _build_network(self):
        """ Create the computational graph
        """
        input_dim = ModuleLoader.batch_builders.get_module().get_input_dim()

        # Placeholders (Use tf.SparseTensor with training=False instead) (TODO: Try restoring dynamic batch_size)
        with tf.name_scope('placeholder_inputs'):
            self.inputs = [
                tf.placeholder(
                    tf.float32,  # -1.0/1.0 ? Probably better for the sigmoid
                    [self.args.batch_size, input_dim],  # TODO: Get input size from batch_builder
                    name='input')
                for _ in range(self.args.sample_length)
                ]
        with tf.name_scope('placeholder_targets'):
            self.targets = [
                tf.placeholder(
                    tf.int32,  # 0/1  # TODO: Int for sofmax, Float for sigmoid
                    [self.args.batch_size,],  # TODO: For softmax, only 1d, for sigmoid, 2d (batch_size, num_class)
                    name='target')
                for _ in range(self.args.sample_length)
                ]
        with tf.name_scope('placeholder_use_prev'):
            self.use_prev = [
                tf.placeholder(
                    tf.bool,
                    [],
                    name='use_prev')
                for _ in range(self.args.sample_length)  # The first value will never be used (always takes self.input for the first step)
                ]

        # Define the network
        self.loop_processing = ModuleLoader.loop_processings.build_module(self.args)
        def loop_rnn(prev, i):
            """ Loop function used to connect one output of the rnn to the next input.
            The previous input and returned value have to be from the same shape.
            This is useful to use the same network for both training and testing.
            Args:
                prev: the previous predicted keyboard configuration at step i-1
                i: the current step id (Warning: start at 1, 0 is ignored)
            Return:
                tf.Tensor: the input at the step i
            """
            next_input = self.loop_processing(prev)

            # On training, we force the correct input, on testing, we use the previous output as next input
            return tf.cond(self.use_prev[i], lambda: next_input, lambda: self.inputs[i])

        # TODO: Try attention decoder/use dynamic_rnn instead
        self.outputs, self.final_state = tf.nn.seq2seq.rnn_decoder(
            decoder_inputs=self.inputs,
            initial_state=None,  # The initial state is defined inside KeyboardCell
            cell=KeyboardCell(self.args),
            loop_function=loop_rnn
        )

        # For training only
        if not self.args.test:
            # Finally, we define the loss function

            # The network will predict a mix a wrong and right notes. For the loss function, we would like to
            # penalize note which are wrong. Eventually, the penalty should be less if the network predict the same
            # note but not in the right pitch (ex: C4 instead of C5), with a decay the further the prediction
            # is (D5 and D1 more penalized than D4 and D3 if the target is D2)

            # For the piano roll mode, by using sigmoid_cross_entropy_with_logits, the task is formulated as a NB_NOTES binary
            # classification problems

            # For the relative note experiment, it use a standard SoftMax where the label is the relative position to the previous
            # note

            self.schedule_policy = Model.ScheduledSamplingPolicy(self.args)
            self.target_weights_policy = Model.TargetWeightsPolicy(self.args)
            self.learning_rate_policy = ModuleLoader.learning_rate_policies.build_module(self.args)  # Load the chosen policies

            # TODO: If train on different length, check that the loss is proportional to the length or average ???
            loss_fct = tf.nn.seq2seq.sequence_loss(
                self.outputs,
                self.targets,
                [tf.constant(self.target_weights_policy.get_weight(i), shape=self.targets[0].get_shape()) for i in range(len(self.targets))],  # Weights
                #softmax_loss_function=tf.nn.softmax_cross_entropy_with_logits,  # Previous: tf.nn.sigmoid_cross_entropy_with_logits TODO: Use option to choose. (new module ?)
                average_across_timesteps=True,  # Before: I think it's best for variables length sequences (specially with the target weights=0), isn't it (it implies also that short sequences are less penalized than long ones) ? (TODO: For variables length sequences, be careful about the target weights)
                average_across_batch=True  # Before: Penalize by sample (should allows dynamic batch size) Warning: need to tune the learning rate
            )
            tf.scalar_summary('training_loss', loss_fct)  # Keep track of the cost

            self.current_learning_rate = tf.placeholder(tf.float32, [])

            # Initialize the optimizer
            opt = tf.train.AdamOptimizer(
                learning_rate=self.current_learning_rate,
                beta1=0.9,
                beta2=0.999,
                epsilon=1e-08
            )

            # TODO: Also keep track of magnitudes (how much is updated)
            self.opt_op = opt.minimize(loss_fct)

    def step(self, batch, train_set=True, glob_step=-1, ret_output=False):
        """ Forward/training step operation.
        Does not perform run on itself but just return the operators to do so. Those have then to be run by the
        main program.
        If the output operator is returned, it will always be the last one on the list
        Args:
            batch (Batch): Input data on testing mode, input and target on output mode
            train_set (Bool): indicate if the batch come from the test/train set (not used when generating)
            glob_step (int): indicate the global step for the schedule sampling
            ret_output (Bool): for the training mode, if true,
        Return:
            Tuple[ops], dict: The list of the operators to run (training_step or outputs) with the associated feed dictionary
        """
        # TODO: Could optimize feeding between train/test/generating (compress code)

        feed_dict = {}
        ops = ()  # For small length, it seems (from my investigations) that tuples are faster than list for merging
        batch.generate(target=False if self.args.test else True)

        # Feed placeholders and choose the ops
        if not self.args.test:  # Training
            if train_set:  # We update the learning rate every x iterations # TODO: What happens when we don't feed the learning rate ??? Stays at the last value ?
                assert glob_step >= 0
                feed_dict[self.current_learning_rate] = self.learning_rate_policy.get_learning_rate(glob_step)

            for i in range(self.args.sample_length):
                feed_dict[self.inputs[i]] = batch.inputs[i]
                feed_dict[self.targets[i]] = batch.targets[i]
                #if np.random.rand() >= self.schedule_policy.get_prev_threshold(glob_step)*self.target_weights_policy.get_weight(i):  # Regular Schedule sample (TODO: Try sampling with the weigths or a mix of weights/sampling)
                if np.random.rand() >= self.schedule_policy.get_prev_threshold(glob_step):  # Weight the threshold by the target weights (don't schedule sample if weight=0)
                    feed_dict[self.use_prev[i]] = True
                else:
                    feed_dict[self.use_prev[i]] = False

            if train_set:
                ops += (self.opt_op,)
            if ret_output:
                ops += (self.outputs,)
        else:  # Generating (batch_size == 1)
            # TODO: What to put for initialisation state (empty ? random ?) ?
            # TODO: Modify use_prev
            for i in range(self.args.sample_length):
                if i < len(batch.inputs):
                    feed_dict[self.inputs[i]] = batch.inputs[i]
                    feed_dict[self.use_prev[i]] = False
                else:  # Even not used, we still need to feed a placeholder
                    feed_dict[self.inputs[i]] = batch.inputs[0]  # Could be anything but we need it to be from the right shape
                    feed_dict[self.use_prev[i]] = True  # When we don't have an input, we use the previous output instead

            ops += (self.loop_processing.get_op(), self.outputs,)  # The loop_processing operator correspond to the recorded softmax sampled

        # Return one pass operator
        return ops, feed_dict
