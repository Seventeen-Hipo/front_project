import numpy as np
import pickle
import os
from torchvision import datasets
from imageio import imwrite

# 数据集放置路径
data_save_pth = "./course_data"
train_pth = os.path.join(data_save_pth, "train")
test_pth = os.path.join(data_save_pth, "test")

# 创建必要的目录
def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

create_dir(train_pth)
create_dir(test_pth)

# 解压路径
data_dir = os.path.join(data_save_pth, "cifar-10-batches-py")

# 数据集下载
def download_data():
    datasets.CIFAR10(root=data_save_pth, train=True, download=True)

# 解压缩数据
def unpickle(file):
    with open(file, "rb") as fo:
        return pickle.load(fo, encoding="bytes")

# 保存图像
def save_images(data, output_dir, offset):
    for i in range(0, 10000):
        img = np.reshape(data[b'data'][i], (3, 32, 32)).transpose(1, 2, 0)
        label = str(data[b'labels'][i])
        label_dir = os.path.join(output_dir, label)
        create_dir(label_dir)

        img_name = f'{label}_{i + offset}.png'
        img_path = os.path.join(label_dir, img_name)
        imwrite(img_path, img)

if __name__ == '__main__':
    download_data()
    for j in range(1, 6):
        path = os.path.join(data_dir, f"data_batch_{j}")
        data = unpickle(path)
        print(f"{path} is loading...")
        save_images(data, train_pth, (j - 1) * 10000)
        print(f"{path} loaded")

    test_data_path = os.path.join(data_dir, "test_batch")
    test_data = unpickle(test_data_path)
    save_images(test_data, test_pth, 0)
    print("test_batch loaded")