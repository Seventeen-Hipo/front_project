import random
from torchvision import  transforms
import torch
import numpy as np

# 设备配置
train_on_gpu = torch.cuda.is_available()
device = torch.device("cuda:0" if train_on_gpu else "cpu")

# 随机种子
# 设置随机种子，可以保证随机结果的可复现性
seed = 42

# 数据路径
data_root = 'course_data'
# 训练所得最佳模型
filename = 'cifar10_best.pt'

# 数据预处理
def get_data_transforms():
    return {
        # 训练集数据增强
        'train': transforms.Compose([
            # 随机裁剪为(32 X 32)大小尺寸的图片
            transforms.RandomCrop(32, padding=4),
            # 随机水平翻转
            transforms.RandomHorizontalFlip(p=0.5),
            # 颜色抖动变换
            transforms.ColorJitter(brightness=0.2, contrast=0.1, saturation=0.1, hue=0.1),
            # 转换为pytorch张量，调整维度顺序，将像素值缩放到0~1之间
            transforms.ToTensor(),
            # 对张量的图像进行标准化，RGB三通道的均值和标准差
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
        ]),
        # 验证集数据增强
        'valid': transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
        ]),
        # 测试集数据增强
        'test': transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
        ])
    }

# 训练参数
# 每个数据的尺寸大小
batch_size = 128
# 第一阶段训练的轮数
num_epochs_phase1 = 10
# 第二阶段训练的轮数
num_epochs_phase2 = 15
# 第一阶段学习率
learning_rate_phase1 = 0.001
# 第二阶段学习率
learning_rate_phase2 = 0.0001

# 设置随机种子
def set_seed(seed):
    # 设置pytorch随机种子
    torch.manual_seed(seed)
    # 设置numpy随机种子
    np.random.seed(seed)
    # 设置python随机种子
    random.seed(seed)
    # 设置所有gpu随机种子
    if train_on_gpu:
        torch.cuda.manual_seed_all(seed)