import tensorflow as tf
import numpy as np
slim = tf.contrib.slim
def residual_block(inputs, num_outputs, is_training):
    with slim.arg_scope([slim.conv2d], kernel_size=3, activation_fn=None, \
        weights_regularizer=slim.l2_regularizer(1e-5)):
        if inputs.shape[-1] != num_outputs:
            out = slim.conv2d(inputs, num_outputs, kernel_size=1)
        else:
            out = inputs
        identity = out
        out = slim.batch_norm(out, is_training=is_training)
        out = tf.nn.relu(out)
        out = slim.conv2d(inputs, num_outputs)
        
        out = slim.batch_norm(out, is_training=is_training)
        out = tf.nn.relu(out)
# out = slim.conv2d(out, num_outputs*4)
        
# out = slim.batch_norm(out, is_training=is_training, activation_fn=tf.nn.relu)
        out = slim.conv2d(out, num_outputs)
        out += identity
        return out
    
def create_cnn_model(height, width, captcha_len=4, vocab_size=62):
    """create a ResNet model to break captcha
    Arguments:
        height -- int, height of the input images
        width -- int, width of the input images
        capthca_len -- int, length of the captcha
        vocab_size -- int, defualt to to ascii letters (A-Za-z) and digits (0-9)
    Returns:
        outs -- output tensor with shape (batch_size, captcha_len, vocab_size)
        placeholders -- dict containing several tf.placeholders
            ---- inputs -- tf.tensor with shape (batch_size, height, width, channel_num)
            ---- is_traning -- tf.bool 
    """
    inputs = tf.placeholder(tf.float32, shape=(None, height, width, 3), name='inputs')
    is_training = tf.placeholder(dtype=tf.bool, shape=(), name='is_training')
    placeholder = {'inputs': inputs, 'is_training': is_training}
    
    with tf.variable_scope('head_conv2d'):
        with slim.arg_scope([slim.conv2d], kernel_size=3, activation_fn=None, \
            weights_regularizer=slim.l2_regularizer(1e-5)):
            out = slim.conv2d(inputs, 32)
            out = slim.conv2d(out, 64)
    for i in range(5):
        with tf.variable_scope('residual_block_{}'.format(i)):
            out = residual_block(out, 64*(i+1), is_training=is_training)
# out = slim.max_pool2d(out, 2, )
    features = tf.reduce_mean(out, (1, 2))
    outs = []
    with slim.arg_scope([slim.fully_connected], activation_fn=None, \
        weights_initializer=tf.truncated_normal_initializer(stddev=0.001), \
        weights_regularizer=slim.l2_regularizer(5e-4)):
        for i in range(captcha_len):
            with tf.variable_scope('dense_{}'.format(i+1)):
                out = slim.fully_connected(features, 512)
                out = slim.batch_norm(out, is_training=is_training, activation_fn=None)
                out = tf.nn.relu(out)
                out = slim.fully_connected(out, vocab_size)
                outs.append(tf.expand_dims(out, axis=1))
    outs = tf.concat(outs, axis=1)
    return outs, placeholder

def create_cnn_single_dense_model(height, width, captcha_len, vocab_size):
    """create a ResNet model to break captcha
    Arguments:
        height -- int, height of the input images
        width -- int, width of the input images
        capthca_len -- int, length of the captcha
        vocab_size -- int, defualt to to ascii letters (A-Za-z) and digits (0-9)
    Returns:
        outs -- output tensor with shape (batch_size, captcha_len, vocab_size)
        placeholders -- dict containing several tf.placeholders
            ---- inputs -- tf.tensor with shape (batch_size, height, width, channel_num)
            ---- is_traning -- tf.bool 
    """
    inputs = tf.placeholder(tf.float32, shape=(None, height, width, 3), name='inputs')
    is_training = tf.placeholder(dtype=tf.bool, shape=(), name='is_training')
    placeholder = {'inputs': inputs, 'is_training': is_training}
    
    with tf.variable_scope('head_conv2d'):
        with slim.arg_scope([slim.conv2d], kernel_size=3, activation_fn=None, \
            weights_regularizer=slim.l2_regularizer(1e-5)):
            out = slim.conv2d(inputs, 32)
            out = slim.conv2d(out, 64)
    for i in range(2):
        with tf.variable_scope('residual_block_{}'.format(i)):
            out = residual_block(out, 128*(i+1), is_training=is_training)
            out = slim.dropout(out, is_training=is_training)
# out = slim.max_pool2d(out, 2, )
    features = tf.reduce_mean(out, (1, 2))
    outs = []
    with slim.arg_scope([slim.fully_connected], activation_fn=None, \
        weights_initializer=tf.truncated_normal_initializer(stddev=0.001), \
        weights_regularizer=slim.l2_regularizer(5e-4)):
        for i in range(captcha_len):
            with tf.variable_scope('dense_{}'.format(i+1)):
                out = slim.fully_connected(features, 512)
                out = slim.batch_norm(out, is_training=is_training, activation_fn=None)
                out = tf.nn.relu(out)
                out = slim.dropout(out, is_training=is_training)
                out = slim.fully_connected(out, vocab_size)
                outs.append(tf.expand_dims(out, axis=1))
    outs = tf.concat(outs, axis=1)
    return outs, placeholder