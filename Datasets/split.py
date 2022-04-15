import shutil

import pandas as pd
from shutil import copyfile
import os

if not os.path.exists("ISIC_2019_Training_Input/MEL"):
    os.makedirs("ISIC_2019_Training_Input/MEL")

if not os.path.exists("ISIC_2019_Training_Input/NV"):
    os.makedirs("ISIC_2019_Training_Input/NV")

if not os.path.exists("ISIC_2019_Training_Input/BCC"):
    os.makedirs("ISIC_2019_Training_Input/BCC")

if not os.path.exists("ISIC_2019_Training_Input/AK"):
    os.makedirs("ISIC_2019_Training_Input/AK")

if not os.path.exists("ISIC_2019_Training_Input/BKL"):
    os.makedirs("ISIC_2019_Training_Input/BKL")

if not os.path.exists("ISIC_2019_Training_Input/DF"):
    os.makedirs("ISIC_2019_Training_Input/DF")

if not os.path.exists("ISIC_2019_Training_Input/VASC"):
    os.makedirs("ISIC_2019_Training_Input/VASC")

if not os.path.exists("ISIC_2019_Training_Input/SCC"):
    os.makedirs("ISIC_2019_Training_Input/SCC")

if not os.path.exists("ISIC_2019_Training_Input/UNK"):
    os.makedirs("ISIC_2019_Training_Input/UNK")

data = pd.read_csv("ISIC_2019_Training_GroundTruth.csv")
row = data.shape[0]

for i in range(row):
    image_name = data["image"][i]
    MEL = data["MEL"][i]
    NV = data["NV"][i]
    BCC = data["BCC"][i]
    AK = data["AK"][i]
    BKL = data["BKL"][i]
    DF = data["DF"][i]
    VASC = data["VASC"][i]
    SCC = data["SCC"][i]
    # UNK = data["UNK"][i]
    try:
        if(MEL == 1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/MEL/{}.jpg".format(image_name))
        elif(NV ==1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/NV/{}.jpg".format(image_name))
        elif(BCC ==1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/BCC/{}.jpg".format(image_name))
        elif(AK ==1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/AK/{}.jpg".format(image_name))
        elif(BKL ==1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/BKL/{}.jpg".format(image_name))
        elif(DF ==1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/DF/{}.jpg".format(image_name))
        elif(VASC ==1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/VASC/{}.jpg".format(image_name))
        elif(SCC ==1):
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/SCC/{}.jpg".format(image_name))
        else:
            shutil.move("ISIC_2019_Training_Input/{}.jpg".format(image_name),
                    "ISIC_2019_Training_Input/UNK/{}.jpg".format(image_name))

    except:
        print("不存在")