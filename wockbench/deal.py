import argparse
from wockbench.utils import *
import os
from tqdm import tqdm
from glob import glob
import time
import numpy as np
from wockbench.net import generator

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def deal_args():
    desc = "Tensorflow implementation of AnimeGAN"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--checkpoint_dir', type=str, default='checkpoint/' + 'model',
                        help='Directory name to save the checkpoints')
    parser.add_argument('--img_file', type=str, default='dataset/test/real',
                        help='Image file to input')
    parser.add_argument('--save_dir', type=str, default='S',
                        help='Directory name to save the result image')

    """checking arguments"""

    return parser.parse_args()


def stats_graph(graph):
    flops = tf.profiler.profile(graph, options=tf.profiler.ProfileOptionBuilder.float_operation())
    # params = tf.profiler.profile(graph, options=tf.profiler.ProfileOptionBuilder.trainable_variables_parameter())
    print('FLOPs: {}'.format(flops.total_float_ops))


def deal(checkpoint_dir, save_dir, img_dir, img_size=None):
    # tf.reset_default_graph()
    if img_size is None:
        img_size = [256, 256]
    result_dir = 'result/' + save_dir
    check_folder(result_dir)
    # test_files = glob('{}/*.*'.format(img_dir))

    # test_real = tf.placeholder(tf.float32, [1, 256, 256, 3], name='test')
    test_real = tf.placeholder(tf.float32, [1, None, None, 3], name='test')

    with tf.variable_scope("generator", reuse=False):
        test_generated = generator.G_net(test_real).fake
    saver = tf.train.Saver()

    gpu_options = tf.GPUOptions(allow_growth=True)
    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=gpu_options)) as sess:
        # tf.global_variables_initializer().run()
        # load model
        ckpt = tf.train.get_checkpoint_state(checkpoint_dir)  # checkpoint file information
        if ckpt and ckpt.model_checkpoint_path:
            ckpt_name = os.path.basename(ckpt.model_checkpoint_path)  # first line
            saver.restore(sess, os.path.join(checkpoint_dir, ckpt_name))
            print(" [*] Success to read {}".format(ckpt_name))
        else:
            print(" [*] Failed to find a checkpoint")
            return

        # FLOPs
        stats_graph(tf.get_default_graph())

        begin = time.time()
        # for sample_file in tqdm(test_files):
        #     # print('Processing image: ' + sample_file)
        #     sample_image = np.asarray(load_test_data(sample_file, img_size))
        #     image_path = os.path.join(result_dir, '{0}'.format(os.path.basename(sample_file)))
        #     fake_img = sess.run(test_generated, feed_dict={test_real: sample_image})
        #     save_images(fake_img, image_path)

        sample_image = np.asarray(load_test_data(img_dir, img_size))
        image_path = os.path.join(result_dir, '{0}'.format(os.path.basename(img_dir)))
        fake_img = sess.run(test_generated, feed_dict={test_real: sample_image})
        save_images(fake_img, image_path)

        end = time.time()
        print(f'deal-time: {end - begin} s')
    return fake_img


if __name__ == '__main__':
    arg = deal_args()
    arg.img_file = "result/real/1.jpg"
    arg.save_dir = "generate"
    print(arg.checkpoint_dir, "\n", arg.img_file, "\n", arg.save_dir)
    deal(arg.checkpoint_dir, arg.save_dir, arg.img_file)
