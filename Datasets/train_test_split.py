import os
import random
import shutil
from shutil import copy2

datadir_normal = "ISIC_2019_Training_Input"

all_data = os.listdir(datadir_normal)
num_all_data = len(all_data)
print("num_all_data: " + str(num_all_data))
index_list = list(range(num_all_data))
# print(index_list)
random.shuffle(index_list)
num = 0

trainDir = "ISIC_2019_Training_Input/train"
if not os.path.exists(trainDir):
    os.mkdir(trainDir)


testDir = 'ISIC_2019_Training_Input/test'
if not os.path.exists(testDir):
    os.mkdir(testDir)

for i in index_list:
    fileName = os.path.join(datadir_normal, all_data[i])
    if num < num_all_data * 0.8:
        # print(str(fileName))
        shutil.move(fileName, trainDir)
    else:
        shutil.move(fileName, testDir)
    num += 1

