#!/usr/local/bin/bash
# To test the model use the following code:
# python run_model.py model=<model> resolution=<resolution> use_gpu=<use_gpu>
# <model> = {iphone, blackberry, sony}
# <resolution> = {orig, high, medium, small, tiny}
# <use_gpu> = {true, false}
# example:  python run_model.py model=iphone resolution=orig use_gpu=true


from scipy import misc
import numpy as np
import tensorflow as tf
from model import resnet
import utils
import os
import sys

# process command arguments
phone, resolution, use_gpu = utils.process_command_args(sys.argv)

# get all available image resolutions
res_sizes = utils.get_resolutions()

# get the specified image resolution
IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_SIZE = utils.get_specified_res(res_sizes, phone, resolution)

# disable gpu if specified
config = tf.ConfigProto(device_count={'GPU': 0}) if use_gpu == "false" else None

# create placeholders for input images
x_ = tf.placeholder(tf.float32, [None, IMAGE_SIZE])
x_image = tf.reshape(x_, [-1, IMAGE_HEIGHT, IMAGE_WIDTH, 3])

# generate enhanced image
enhanced = resnet(x_image)

with tf.Session(config=config) as sess:

    # load pre-trained model
    saver = tf.train.Saver()
    saver.restore(sess, "/gdata/huangjie/DanfanDemo/models/" + phone)

    test_dir = "/gdata/huangjie/DanfanDemo/test_photos/" + phone + "/"
    test_photos = [f for f in os.listdir(test_dir) if os.path.isfile(test_dir + f)]

    for photo in test_photos:

        # load training image and crop it if necessary

        print("Processing image " + photo)
        image = np.float16(misc.imresize(misc.imread(test_dir + photo), res_sizes[phone])) / 255

        image_crop = utils.extract_crop(image, resolution, phone, res_sizes)
        image_crop_2d = np.reshape(image_crop, [1, IMAGE_SIZE])

        # get enhanced image

        enhanced_2d = sess.run(enhanced, feed_dict={x_: image_crop_2d})
        enhanced_image = np.reshape(enhanced_2d, [IMAGE_HEIGHT, IMAGE_WIDTH, 3])

        before_after = np.hstack((image_crop, enhanced_image))
        photo_name = photo.rsplit(".", 1)[0]

        # save the results as .png images

        # misc.imsave("/gdata/huangjie/DanfanDemo/results/" + photo_name + "_original.jpg", image_crop)
        # misc.imsave("/gdata/huangjie/DanfanDemo/results/" + photo_name + "_processed.png", enhanced_image)
        misc.imsave("/gdata/huangjie/DanfanDemo/results/" + photo_name + ".png", enhanced_image)
 
