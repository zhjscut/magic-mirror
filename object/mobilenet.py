import sys
sys.path.append('/mnt/b1/archive/models/research/slim')
from nets.mobilenet import mobilenet_v2
import tensorflow as tf
from datasets import imagenet

checkpoint = '/mnt/b1/pretrained_models/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224.ckpt'

def getMobileNet(checkpoint):
    graph = tf.Graph()
    sess = tf.Session(graph=graph)
    with graph.as_default():
        file_input = tf.placeholder(tf.string, ())
        image = tf.image.decode_image(tf.read_file(file_input))
        images = tf.expand_dims(image, 0)
        images = tf.cast(images, tf.float32) / 128. - 1
        images.set_shape((None, None, None, 3))
        images = tf.image.resize_images(images, (224, 224))    
        with tf.contrib.slim.arg_scope(mobilenet_v2.training_scope(is_training=False)):
            logits, endpoints = mobilenet_v2.mobilenet(images)
        ema = tf.train.ExponentialMovingAverage(0.999)
        vars = ema.variables_to_restore()
        saver = tf.train.Saver(vars)
        saver.restore(sess, checkpoint)
    return sess, graph, endpoints, file_input

def predict(image_filename):
    sess, graph, endpoints, file_input = getMobileNet(checkpoint)
    label_map = imagenet.create_readable_names_for_imagenet_labels()
    x = endpoints['Predictions'].eval(session=sess, feed_dict={file_input: image_filename})
    argmax = x.argsort()[:, -5:][:, ::-1].tolist()[0]
    res = {}
    for i, index in enumerate(argmax):
        res['top{}'.format(i+1)] = {'label': label_map[index], 'confidence': '{:.4f}'.format(x[0][index])}
    return res

if __name__ == '__main__':
    image_filename = sys.argv[1]
    print(predict(image_filename))
