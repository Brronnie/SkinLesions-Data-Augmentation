import cv2
import os

def cut_image(file_name, in_img_path, out_dir):
    img = cv2.imread(in_img_path)
    # 新裁剪图片的高度
    new_img_height = 700
    # 获得图片的高度和宽度
    img_height, img_width, _ = img.shape
    temp_height = 0

    i = 1
    while temp_height < img_height:
        # 裁剪坐标为[y0:y1, x0:x1]
        size = img[temp_height:temp_height + new_img_height, 0:img_width]

        # 图片最后结尾长度不够
        if temp_height > img_height:
            size = img[temp_height - new_img_height:img_height, 0:img_width]

        # 保存图片
        if i == 1:
            cv2.imwrite(os.path.join(out_dir, file_name), size)
        i = i + 1

        # 向下移动高度
        temp_height = temp_height + new_img_height

if __name__ == '__main__':
    count = 0
    for root, dir, filename in os.walk("Humanae"):
        for image in filename:
            if image != ".DS_Store":
                count += 1
                if count < 10:
                    file = "Color_0" + str(count) + ".jpg"
                else:
                    file = "Color_" + str(count) + ".jpg"
                in_path = "Humanae/" + str(image)
                out_path = "SkinColors"
                cut_image(file, in_path, out_path)