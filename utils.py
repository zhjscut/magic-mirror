import numpy as np
import pickle
import string
import os
from matplotlib import pyplot as plt

def captcha_to_onehot(captcha, vocab, captcha_len=4):
    """turns captcha to onehot encoding
    Arguments:
        captcha -- np.array with shape (batch_size, captcha_len)
        vocab -- default to be 62 (ascii letters and digits)
        captcha_len -- integer to specify the length of the captcha
    Returns:
        onehots -- np.array with shape (batch_size, captcha_len, vocab_size)
    """
    onehots = []
    dictionary = np.array(list(vocab))
    vocab_size = len(vocab)
    for i in range(captcha_len):
        onehot = np.zeros((captcha.shape[0], vocab_size), dtype=np.float32)
        onehot[captcha[:, i].reshape((-1, 1))==dictionary] = 1.
        onehots.append(np.expand_dims(onehot, axis=1))
    onehots = np.concatenate(onehots, axis=1)
    return onehots

def load_data(dataset='crawled', images_path=None):
    data_all = []
    labels_all = []
    if dataset=='crawled':
        if images_path==None:
            images_path = './images'
        for filename in os.listdir(images_path):
            data_all.append(plt.imread(os.path.join(images_path, filename), 'gif')[:, :, :3])
            labels_all.append(np.array(filename[:-4]))
        data_all = np.expand_dims(data_all, 0)
        labels_all = np.expand_dims(labels_all, 0)
    if dataset=='generated':
        for i in range(1, 2):
            with open('images_captcha_{}.data'.format(i), 'rb') as f:
                data = pickle.load(f)
            with open('labels_captcha_{}.data'.format(i), 'rb') as f:
                labels = pickle.load(f)
            data_all.append(data)
            labels_all.append(labels)
    data_all = np.concatenate(tuple(data_all), axis=0)
    labels_all = np.concatenate(tuple(labels_all), axis=0)
    return data_all, labels_all

def clip_images(images, bounds= \
    [(3, 19, 0, 20), (15, 31, 0, 20), (27, 43, 0, 20), (39, 55, 0, 20)]):
    """clip images with bounds
    Arguments:
        iamges: ndarray with shape (batch_size, height, width, channels)
        bounds: list, each element is a tuple with 4 elements, 
            corresponding to left, right, top, bottom bound respectively
    Returns:
        res: list with length equal to len(bounds), 
            each element is a ndarray with shape (batch_size, height, width, channels)
    """
    res = []
    for bound in bounds:
        assert len(bound)==4
        left, right, top, bottom = bound
        res.append(images[:, top: bottom+1, left: right+1, :])
    return res