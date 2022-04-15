from PIL import Image
from math import floor
import numpy as np
import time
import cv2 as cv
import os

from keras.models import model_from_json, Model
from SL_StyleGAN import GAN
from AdaIN import AdaInstanceNormalization, InstanceNormalization
from data_loader import data_generator

from train import *

# 一般情况下采用该代码能够解决问题，可以发现函数返回结果已经转化成tensorflow.python.framework.ops.Tensor类了
from tensorflow.python.framework.ops import disable_eager_execution

disable_eager_execution()

index = [AK, BCC, BKL, DF, MEL, NV, SCC, VASC] = [0, 1, 2, 3, 4, 5, 6, 7]
cancer_name = ["AK", "BCC", "BKL", "DF", "MEL", "NV", "SCC", "VASC"]
cancer_type = VASC
evaluate_file = "Evaluated/VASC"
generate_file = "Generated/VASC"
skin_data = "Datasets/SkinColors"

# 1<=skin_color<=42
# if no extra skin color, skin_color = None
skin_color = 5

if __name__ == "__main__":

    model = Train()

    model.load_generator(cancer_name[cancer_type])

    # Evaluate the generator
    model.evaluate_generator(evaluate_file)

    # Generate images
    model.generator_generate_images(generate_file, num=500, skin_color=skin_color)
