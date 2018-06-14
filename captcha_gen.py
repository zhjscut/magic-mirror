#!/usr/bin/python
# -!-encoding=UTF-8-!-
from captcha.image import ImageCaptcha  # pip install captcha
import numpy as np
import pickle
import matplotlib.pyplot as plt
from PIL import Image
import random
import string
import os
import _thread

vacab_set = np.array(list(string.digits+string.ascii_letters))

def random_captcha_text(char_set=vacab_set, \
    captcha_size=4, num=1):
    """utility function to generate text for captcha
    returns:
        captcha_text: np.array of shape (num, capcha_size)
    """
    index = np.random.randint(0, len(vacab_set), (num, captcha_size))
    captcha_text = char_set[index].view(\
        'U{}'.format(captcha_size)).squeeze(axis=1)
    return captcha_text

def gen_captcha_text_and_image(num=1):
    """generate captcha image randomly
    Arguments:
        num -- integer, specify the number of \
            images to be generated, default 1
    Return:
        texts -- np.array with shape (num, captcha_size)
        images -- np.array with shape (num, 60, 160, 3)
    """
    image = ImageCaptcha()

    captcha_texts = random_captcha_text(num=num)
    captcha_images = []
    for i in range(num):
        captcha = image.generate(captcha_texts[i])
        captcha_image = Image.open(captcha)
        captcha_image = np.array(captcha_image)
        captcha_images.append(captcha_image)
    return captcha_texts, np.array(captcha_images)

def gen_data_and_save(num, filename):
    print("Filename {} generating...".format(filename))
    labels, data = gen_captcha_text_and_image(num)
    with open('images_'+filename, 'wb') as f:
        pickle.dump(data, f)
    with open('labels_'+filename, 'wb') as f:
        pickle.dump(labels, f)
    print("Filename {} done!".format(filename))

if __name__ == '__main__':
    batch_num = 50000
    print("Generating...")
    for i in range(5, 10):
        _thread.start_new_thread(gen_data_and_save,\
            (int(batch_num), 'captcha_{}.data'.format(i+1)))
    while True:
        pass
