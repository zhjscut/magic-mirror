# -!- coding: utf-8 -!- import os
import tensorflow as tf
import numpy as np
slim = tf.contrib.slim
from utils import load_data, captcha_to_onehot, clip_images
from models import create_cnn_model, create_cnn_single_dense_model
# from captcha_gen import gen_captcha_text_and_image
import sys
import string
from matplotlib import pyplot as plt
import os
import pprint

height = 24
width = 15

vocab = string.digits + string.ascii_lowercase
vocab_size = len(vocab) # ascii letters and digits
vocab_size = 36
captcha_len = 1
lr = 5e-4
epochs_num = 500
batch_size = 32
bounds = [(3, 17, 1, 24), (15, 29, 1, 24), (27, 41, 1, 24), (39, 53, 1, 24)]

model_name = 'breaker_cnn_single_dense_adam'
logdir = os.path.join('./log', model_name)
if not tf.gfile.Exists(logdir):
    tf.gfile.MkDir(logdir)

checkpointdir = os.path.join('./checkpoint', model_name)
if not tf.gfile.Exists(checkpointdir):
    tf.gfile.MkDir(checkpointdir)

def train(learning_rate=lr, \
          model_name=model_name, \
          restore=False ,\
          logdir=logdir, \
          batch_size=batch_size, \
          epochs_num=epochs_num, \
          checkpointdir=checkpointdir):
    graph = tf.Graph()
    sess = tf.Session(graph=graph)
    with graph.as_default():
        # training set
        data, labels = load_data(images_path='./images')
        data = clip_images(data, bounds=bounds)
        data = np.concatenate(data, axis=0)
        labels = labels.view('U1').reshape(-1, 4).T.reshape((-1))
        labels = np.expand_dims(labels, axis=1)
        print('Training set size: {}'.format(data.shape[0]))
        
        # validation set
        test_images, test_labels = load_data(images_path='./images_set2')
        test_images = clip_images(test_images, bounds=bounds)
        test_images = np.concatenate(test_images, axis=0)
        test_labels = test_labels.view('U1').reshape(-1, 4).T.reshape((-1))
        test_labels = np.expand_dims(test_labels, axis=1)
        print('Validation set size: {}'.format(test_images.shape[0]))
        
        labels_placeholder = tf.placeholder(tf.float32, \
            (None, captcha_len, vocab_size), 'labels_inputs')
        istraining_placeholder = tf.placeholder(tf.bool, (), 'is_traning')
        learning_rate_placeholder = tf.placeholder(tf.float32, (), 'learning_rate')
        outs, placeholders = create_cnn_single_dense_model(height, width, \
            captcha_len=1, vocab_size=vocab_size)
        
        print('***********************Trainable Variables*************************')
        pprint.pprint(tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES))
        print('*******************************************************************')
        
        pred = tf.argmax(outs, axis=2)
        ground_truth = tf.argmax(labels_placeholder, axis=2)
        accuracy = tf.reduce_sum(tf.cast(tf.equal(\
            pred, ground_truth), tf.float32)) / batch_size / captcha_len
        
        loss_sum = 0.
        for i in range(captcha_len):
            loss = tf.reduce_sum(tf.nn.softmax_cross_entropy_with_logits_v2(\
                labels=labels_placeholder[:, i, :], logits=outs[:, i, :]))
            loss_sum += loss
        print(tf.get_collection(tf.GraphKeys.UPDATE_OPS))
        optimizer = tf.train.AdamOptimizer(learning_rate= \
            learning_rate_placeholder)
#         optimizer = tf.train.GradientDescentOptimizer(learning_rate = \
#             learning_rate_placeholder)
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies([tf.group(*update_ops)]):
            trian_op = optimizer.minimize(loss_sum)
        summary_writer = tf.summary.FileWriter(logdir)
        tf.summary.scalar('accuracy', accuracy)
        tf.summary.scalar('loss', loss)
        tf.summary.image('input_images', placeholders['inputs'])
        tf.summary.tensor_summary('labels', labels_placeholder)
        tf.summary.histogram('input_images_his', placeholders['inputs'])
        for var in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES):
            tf.summary.histogram(var.name, var)
        merged = tf.summary.merge_all()
        
        saver = tf.train.Saver()
        if restore:
            saver.restore(sess, tf.train.latest_checkpoint(checkpointdir))
        else:
            sess.run(tf.global_variables_initializer())
        feed_dict = {learning_rate_placeholder: learning_rate, \
            placeholders['is_training']: True}
        iteration = 0
        for i in range(epochs_num):
            permutation = np.random.permutation(data.shape[0])
            data = data[permutation]
            labels = labels[permutation]
            for j in range(data.shape[0]//batch_size):
                iteration += 1
                feed_dict[placeholders['inputs']] = data[ \
                    j*batch_size:(j+1)*batch_size] / 255.
                feed_dict[labels_placeholder] = captcha_to_onehot(\
                        labels[j*batch_size:(j+1)*batch_size].view(\
                            'U1').reshape((-1, captcha_len)), \
                    vocab, captcha_len)

                sess.run([trian_op], feed_dict=feed_dict)
                if j%50==0:
                    merged_res = sess.run(merged, feed_dict=feed_dict)
                    summary_writer.add_summary(merged_res, iteration)
                    loss_res, accuracy_res = sess.run([loss, accuracy], feed_dict=feed_dict)
                    print('Epochs: {} Iteration: {} Loss: {}, Accuracy: {}'.format(\
                        i, j, loss_res, accuracy_res))
            saver.save(sess, os.path.join(checkpointdir, model_name), i)
            test_accuracy = 0.
            for k in range(test_images.shape[0]//batch_size):
                feed_dict[placeholders['inputs']] = test_images[ \
                    k*batch_size:(k+1)*batch_size] / 255.
                feed_dict[labels_placeholder] = captcha_to_onehot(\
                        test_labels[k*batch_size:(k+1)*batch_size].view(\
                            'U1').reshape((-1, captcha_len)), \
                    vocab, captcha_len)
                feed_dict[placeholders['is_training']] = False
                test_accuracy += sess.run(accuracy, feed_dict=feed_dict)
            feed_dict[placeholders['is_training']] = True
            print('Accuracy on test set: {}'.format(test_accuracy/(test_images.shape[0]//batch_size)))
            if i%50==0:
                learning_rate = learning_rate / 5
                feed_dict[learning_rate_placeholder] = learning_rate
    sess.close()

def predict(inputs):
    """inference function
    Arguments:
        inputs -- np.array with shape (batch_size, height, width, 3)
    Returns:
        pred_res -- np.array with shape (batch_size, captcha_len)
    """
    graph = tf.Graph()
    sess = tf.Session(graph=graph)
    with graph.as_default():
        outs, placeholders = create_cnn_single_dense_model(height, width, \
            captcha_len=1, vocab_size=vocab_size)
        pred = tf.argmax(outs, axis=2)
        feed_dict = {placeholders['is_training']: False,  \
                     placeholders['inputs']: inputs}
        saver = tf.train.Saver()
        saver.restore(sess, tf.train.latest_checkpoint(checkpointdir))
        pred_res = sess.run(pred, feed_dict=feed_dict)
        return np.array(list(vocab))[pred_res]

def break_captcha(captcha_images):
    """predict captcha images from Zhengfang system using single character CNN
    Arguments:
        captcha_images -- ndarray with shape (height, width, 3), scale 0 to 1
    Return:
        res -- str with length 4
    """
    clipped_images = clip_images(np.expand_dims(captcha_images, axis=0), bounds=bounds)
    clipped_images = np.concatenate(clipped_images, axis=0)
    res = predict(clipped_images)
    res = res.reshape((-1)).view('U4').tolist()[0]
    return res
