import os
import random
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn
from torchvision import datasets, transforms, models
from torchvision.models import ResNet18_Weights
from PIL import Image, ImageDraw, ImageFont

# 解决 OpenMP 冲突
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 设备配置（自动适配）
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('使用 GPU' if torch.cuda.is_available() else '使用 CPU')

# 随机种子（复现性）
# seed = 50
# torch.manual_seed(seed)
# np.random.seed(seed)
# random.seed(seed)
# if torch.cuda.is_available():
#     torch.cuda.manual_seed_all(seed)

# 数据预处理（与训练一致）
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.1, 0.1, 0.1),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ]),
    'valid': transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ]),
    'test': transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
}

# 配置参数
batch_size = 128
# 数据集路径
data_root = './course_data'
# 模型权重
weight_path = 'cifar10_best.pt'
# 测试图片数量
num_test_images = 10

# 强制中文字体路径
font_path = "C:/Windows/Fonts/simhei.ttf" if os.name == 'nt' else "/System/Library/Fonts/PingFang.ttc"


# 加载数据集
def load_datasets():
    # 异常处理
    try:
        train_dataset = datasets.ImageFolder(
            os.path.join(data_root, 'train'),
            transform=data_transforms['train']
        )
        train_size = int(0.8 * len(train_dataset))
        valid_size = len(train_dataset) - train_size
        train_dataset, valid_dataset = torch.utils.data.random_split(
            train_dataset, [train_size, valid_size]
        )
        valid_dataset.dataset.transform = data_transforms['valid']

        test_dataset = datasets.ImageFolder(
            os.path.join(data_root, 'test'),
            transform=data_transforms['test']
        )

        dataloaders = {
            'train': torch.utils.data.DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True, num_workers=4
            ),
            'valid': torch.utils.data.DataLoader(
                valid_dataset, batch_size=batch_size, shuffle=False, num_workers=4
            ),
            'test': torch.utils.data.DataLoader(
                test_dataset, batch_size=batch_size, shuffle=False, num_workers=4
            )
        }

        dataset_sizes = {
            'train': len(train_dataset),
            'valid': len(valid_dataset),
            'test': len(test_dataset)
        }

        class_names = train_dataset.dataset.classes
        return dataloaders, dataset_sizes, class_names, test_dataset
    except FileNotFoundError as e:
        print(f"错误：数据集路径无效 - {e}")
        print("请检查 data_root，确保包含 train/test 文件夹")
        exit(1)


# 初始化模型
def initialize_model(num_classes):
    try:
        model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        for param in model.parameters():
            param.requires_grad = False

        # 替换分类头
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_ftrs, num_classes)
        )
        return model.to(device)
    except Exception as e:
        print(f"模型初始化失败: {e}")
        exit(1)


# 预测并可视化（彻底修复显示问题）
def predict_and_show_random_images(model, test_dataset, class_names, num_images=5):
    model.eval()
    indices = random.sample(range(len(test_dataset)), num_images)
    plt.figure(figsize=(10, 5 * num_images))  # 增大高度，避免挤压

    # 强制加载中文字体（解决乱码）
    try:
        font = ImageFont.truetype(font_path, 10)  # 增大字体
    except:
        font = ImageFont.load_default()
        print("警告：中文字体加载失败，使用默认字体")

    for i, idx in enumerate(indices):
        image, true_label = test_dataset[idx]
        image_tensor = image.unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image_tensor)
            preds = torch.argmax(outputs, dim=1)
            probs = torch.softmax(outputs, dim=1)

        # 还原图像（解决颜色异常）
        image_np = image_tensor.squeeze().cpu().numpy().transpose((1, 2, 0))
        mean = np.array([0.4914, 0.4822, 0.4465])
        std = np.array([0.2023, 0.1994, 0.2010])
        image_np = std * image_np + mean
        image_np = np.clip(image_np, 0, 1)

        # 转换为 PIL 图像（确保类型正确）
        pil_image = Image.fromarray((image_np * 255).astype(np.uint8))
        draw = ImageDraw.Draw(pil_image)

        # 构造文本（解决布局问题）
        true_class = class_names[true_label]
        pred_class = class_names[preds.item()]
        pred_prob = probs[0][preds.item()].item() * 100

        # 颜色配置（确保对比明显）
        if true_label == preds.item():
            text_color = (0, 255, 0)  # 亮绿色
            result = "正确"
        else:
            text_color = (255, 0, 0)  # 亮红色
            result = "错误"

        # 文本内容（换行符适配）
        # 结果，预测，正确
        text = (f"{result}\n，{pred_class}，{true_class}")

        # 绘制文本（调整位置，避免超出边界）
        draw.multiline_text((1, 10), text, font=font, fill=text_color, align="left")

        # 显示图片（子图布局）
        plt.subplot(num_images, 1, i + 1)
        plt.imshow(pil_image)
        plt.axis('off')  # 隐藏坐标轴

    plt.tight_layout(pad=3)  # 增加子图间距
    plt.show()


# 主流程（完整调用）
if __name__ == '__main__':
    print("加载数据集...")
    dataloaders, dataset_sizes, class_names, test_dataset = load_datasets()
    print(f"类别: {class_names}")

    print("初始化模型...")
    model = initialize_model(len(class_names))

    if os.path.exists(weight_path):
        print(f"加载预训练模型: {weight_path}")
        # 自动适配设备加载
        checkpoint = torch.load(weight_path, map_location=device)
        model.load_state_dict(checkpoint['state_dict'])
    else:
        print("错误：未找到模型权重文件")
        exit(1)

    print(f"预测并展示 {num_test_images} 张图片...")
    predict_and_show_random_images(
        model,
        test_dataset,
        class_names,
        num_images=num_test_images
    )