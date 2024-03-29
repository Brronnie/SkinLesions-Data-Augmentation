from PIL import Image
from math import floor
import numpy as np
import time
import cv2 as cv
import os
import shutil

from keras.models import model_from_json, Model
from SL_StyleGAN import GAN
from AdaIN import AdaInstanceNormalization, InstanceNormalization
from data_loader import data_generator
from color_transfer import color_transfer

# 一般情况下采用该代码能够解决问题，可以发现函数返回结果已经转化成tensorflow.python.framework.ops.Tensor类了
from tensorflow.python.framework.ops import disable_eager_execution
disable_eager_execution()

# Para setting
im_size = 256
latent_size = 100
batch_size = 16
directory = "ISIC_2019_Training_Input/NV"
# AK: 867, SCC: 628, VASC: 253, DF: 239, NV: 12875
n_images = 12875
target_file = "Results/NV/train11"
suff = 'jpg'

if not os.path.exists(target_file):
    os.mkdir(target_file)

# Style Z
def noise(n):
    return np.random.normal(0.0, 1.0, size=[n, latent_size])


# Noise Sample
def noise_image(n):
    return np.random.normal(0.0, 1.0, size=[n, im_size, im_size, 1])


class Train(object):

    def __init__(self, steps=-1, lr=0.0001, silent=True):

        self.GAN = GAN(lr=lr)
        self.DisModel = self.GAN.DisModel()
        self.AdModel = self.GAN.AdModel()
        self.generator = self.GAN.generator()

        if steps >= 0:
            self.GAN.steps = steps

        self.lastblip = time.perf_counter()
        # self.lastblip = time.clock()

        self.noise_level = 0

        # load image data
        self.im = data_generator(im_size, directory, n_images, suffix=suff, flip=True)

        self.silent = silent

        self.ones = np.ones((batch_size, 1), dtype=np.float32)
        self.zeros = np.zeros((batch_size, 1), dtype=np.float32)
        self.nones = -self.ones

        self.enoise = noise(8)
        self.enoiseImage = noise_image(8)

    def train(self):

        # Train Alternating
        a = self.train_dis()
        b = self.train_gen()

        # Print information when training
        if self.GAN.steps % 20 == 0 and not self.silent:
            print("\n\nRound " + str(self.GAN.steps) + ":")
            print("D: " + str(a))
            print("G: " + str(b))
            s = round((time.perf_counter() - self.lastblip) * 1000) / 1000
            print("T: " + str(s) + " sec")
            self.lastblip = time.perf_counter()

            # Save Model
            if self.GAN.steps % 500 == 0:
                self.save(floor(self.GAN.steps / 10000)+0)
            if self.GAN.steps % 500 == 0:
                self.evaluate(floor(self.GAN.steps / 100)+0)

        self.GAN.steps = self.GAN.steps + 1

    def train_dis(self):

        # Get Data
        train_data = [self.im.get_batch(batch_size), noise(batch_size), noise_image(batch_size), self.ones]

        # Train
        d_loss = self.DisModel.train_on_batch(train_data, [self.ones, self.nones, self.ones])

        return d_loss

    def train_gen(self):

        # Train
        g_loss = self.AdModel.train_on_batch([noise(batch_size), noise_image(batch_size), self.ones], self.zeros)

        return g_loss

    def transfer(self, source, target):
        transfer = color_transfer(source, target)
        return transfer

    def evaluate(self, num=0):  # 8x4 images, bottom row is constant

        n = noise(32)
        n2 = noise_image(32)

        im2 = self.generator.predict([n, n2, np.ones([32, 1])])
        im3 = self.generator.predict([self.enoise, self.enoiseImage, np.ones([8, 1])])

        r12 = np.concatenate(im2[:8], axis=1)
        r22 = np.concatenate(im2[8:16], axis=1)
        r32 = np.concatenate(im2[16:24], axis=1)
        r43 = np.concatenate(im3[:8], axis=1)

        c1 = np.concatenate([r12, r22, r32, r43], axis=0)

        x = Image.fromarray(np.uint8(c1 * 255))

        x.save(target_file + "/SL-StyleGAN_evaluated_" + str(num) + ".jpg")

    # Save Models
    def saveModel(self, model, name, num):
        json = model.to_json()
        with open("SavedModels/" + name + ".json", "w") as json_file:
            json_file.write(json)

        model.save_weights("SavedModels/" + name + "_" + str(num) + ".h5")

    # Load Models
    def loadModel(self, name, num):  # Load a Model

        file = open("SavedModels/" + name + ".json", 'r')
        json = file.read()
        file.close()

        mod = model_from_json(json, custom_objects={'AdaInstanceNormalization': AdaInstanceNormalization
                                                    })
        mod.load_weights("SavedModels/" + name + "_" + str(num) + ".h5")

        return mod

    def loadToGenerate(self, cancer_name, filename):  # Load a Model

        file = open("Generators/" + cancer_name + "/" + filename + ".json", 'r')
        json = file.read()
        file.close()

        mod = model_from_json(json, custom_objects={'AdaInstanceNormalization': AdaInstanceNormalization
                                                    })
        mod.load_weights("Generators/" + cancer_name + "/" + filename + ".h5")

        return mod

    # Save JSON and Weights into /SavedModels/
    def save(self, num):
        self.saveModel(self.GAN.G, "generator", num)
        self.saveModel(self.GAN.D, "discriminator", num)

    # Load JSON and Weights from /SavedModels/
    def load(self, num):  # Load JSON and Weights from /Models/
        steps1 = self.GAN.steps

        self.GAN = None
        self.GAN = GAN()

        # Load Models
        self.GAN.G = self.loadModel("generator", num)
        self.GAN.D = self.loadModel("discriminator", num)

        self.GAN.steps = steps1

        self.generator = self.GAN.generator()
        self.DisModel = self.GAN.DisModel()
        self.AdModel = self.GAN.AdModel()

        # Load JSON and Weights from /Generators/
    def load_generator(self, cancer_name):  # Load JSON and Weights from /Models/
        steps1 = self.GAN.steps

        self.GAN = None
        self.GAN = GAN()

        # Load Models
        self.GAN.G = self.loadToGenerate(cancer_name, "generator")
        self.GAN.D = self.loadToGenerate(cancer_name, "discriminator")

        self.GAN.steps = steps1

        self.generator = self.GAN.generator()
        self.DisModel = self.GAN.DisModel()
        self.AdModel = self.GAN.AdModel()

    def evaluate_generator(self, path, skin_color=None):
        n = noise(32)
        n2 = noise_image(32)

        im2 = self.generator.predict([n, n2, np.ones([32, 1])])
        im3 = self.generator.predict([self.enoise, self.enoiseImage, np.ones([8, 1])])

        r12 = np.concatenate(im2[:8], axis=1)
        r22 = np.concatenate(im2[8:16], axis=1)
        r32 = np.concatenate(im2[16:24], axis=1)
        r43 = np.concatenate(im3[:8], axis=1)

        c1 = np.concatenate([r12, r22, r32, r43], axis=0)

        x = Image.fromarray(np.uint8(c1 * 255))
        x.save(path + "/Evaluated_SkinColor=None.jpg")

        if skin_color == None:
            for i in range(1, 43):
                if i < 10 and i > 0:
                    source = cv.imread("Datasets/SkinColors/Color_0" + str(i) + ".jpg")
                    target = cv.imread(path + "/Evaluated_SkinColor=None.jpg")
                    cv.imwrite(path + "/Evaluated_SkinColor=0" + str(i) + ".jpg", self.transfer(source, target))
                elif i >= 10:
                    source = cv.imread("Datasets/SkinColors/Color_" + str(i) + ".jpg")
                    target = cv.imread(path + "/Evaluated_SkinColor=None.jpg")
                    cv.imwrite(path + "/Evaluated_SkinColor=" + str(i) + ".jpg", self.transfer(source, target))
        elif skin_color < 10 and skin_color > 0:
            source = cv.imread("Datasets/SkinColors/Color_0" + str(skin_color) + ".jpg")
            target = cv.imread(path + "/Evaluated_SkinColor=None.jpg")
            cv.imwrite(path + "/Evaluated_SkinColor=0" + str(skin_color) + ".jpg", self.transfer(source, target))
        elif skin_color >= 10:
            source = cv.imread("Datasets/SkinColors/Color_" + str(skin_color) + ".jpg")
            target = cv.imread(path + "/Evaluated_SkinColor=None.jpg")
            cv.imwrite(path + "/Evaluated_SkinColor=" + str(skin_color) + ".jpg", self.transfer(source, target))


    def generator_generate_images(self, path, num, skin_color=None):
        num_img = num  # num of images to generate
        rnd_n = np.random.RandomState(6)
        n = rnd_n.normal(0.0, 1.0, size=[num_img, latent_size])
        # n[:, 1] = 2.5
        rnd_img = np.random.RandomState(8)
        n_img = rnd_img.normal(0.0, 1.0, size=[num_img, im_size, im_size, 1])

        gen_imgs = self.generator.predict([n, n_img, np.ones([num_img, 1])])

        for k in range(num_img):
            gen_imgs[k] = cv.normalize(gen_imgs[k], None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
            (b, g, r) = cv.split(gen_imgs[k])
            gen_imgs[k] = cv.merge([r, g, b])
            if skin_color == None:
                cv.imwrite(path + "/Generated_SkinColor=None_%d.jpg" % (k + 1), gen_imgs[k])
            elif skin_color < 10:
                cv.imwrite("Cache/Generated_SkinColor=None_%d.jpg" % (k + 1), gen_imgs[k])
                target = cv.imread("Cache/Generated_SkinColor=None_%d.jpg" % (k + 1))
                transfer = self.transfer(source=cv.imread("Datasets/SkinColors/Color_0" + str(skin_color) + ".jpg"),
                                         target=target)
                cv.imwrite(path + "/Generated_SkinColor=" + str(skin_color) + "_%d.jpg" % (k + 1), transfer)
            else:
                cv.imwrite("Cache/Generated_SkinColor=None_%d.jpg" % (k + 1), gen_imgs[k])
                target = cv.imread("Cache/Generated_SkinColor=None_%d.jpg" % (k + 1))
                transfer = self.transfer(source=cv.imread("Datasets/SkinColors/Color_" + str(skin_color) + ".jpg"),
                                         target=target)
                cv.imwrite(path + "/Generated_SkinColor=" + str(skin_color) + "_%d.jpg" % (k + 1), transfer)

        shutil.rmtree("Cache")
        os.mkdir("Cache")

    def generate_images(self):
        num_img = 500  # num of images to generate
        rnd_n = np.random.RandomState(6)
        n = rnd_n.normal(0.0, 1.0, size=[num_img, latent_size])
        # n[:, 1] = 2.5
        rnd_img = np.random.RandomState(8)
        n_img = rnd_img.normal(0.0, 1.0, size=[num_img, im_size, im_size, 1])

        gen_imgs = self.generator.predict([n, n_img, np.ones([num_img, 1])])

        for k in range(num_img):
            gen_imgs[k] = cv.normalize(gen_imgs[k], None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
            (b, g, r) = cv.split(gen_imgs[k])
            gen_imgs[k] = cv.merge([r, g, b])
            cv.imwrite(target_file + "/SL-StyleGAN_generated_%d.jpg" % (k + 1), gen_imgs[k])



if __name__ == "__main__":
    epoch = 20000

    model = Train(lr=0.0002, silent=False)        # lr = 0.001 bad results

    # This is for the model loading and evaluating, or continue training
    # model.load(0)

    for i in range(epoch):
        model.train()

    # Generate images
    model.generate_images()

