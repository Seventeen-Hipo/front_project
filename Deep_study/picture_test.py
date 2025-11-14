import os
import torch
from torch import nn
from torchvision import datasets, transforms, models
from torchvision.models import ResNet18_Weights
from PIL import Image
import matplotlib.pyplot as plt

# 解决 OpenMP 冲突
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 设备配置
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(f'运行设备: {device}')

# 数据预处理（与训练时保持一致）
data_transforms = {
    'test': transforms.Compose([
        transforms.Resize((32, 32)),  # 调整为模型输入尺寸
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
}

# 配置参数
# 模型权重路径
weight_path = '../cifar10_best.pt'
# CIFAR-10类别
class_names = ['飞机', '汽车', '鸟', '猫', '鹿','狗', '青蛙', '马', '船', '卡车']
# 初始化模型
def initialize_model(num_classes):
    """加载预训练模型并替换分类头"""
    try:
        # 加载预训练的ResNet18模型
        model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

        # 冻结所有参数（仅微调分类头）
        for param in model.parameters():
            param.requires_grad = False

        # 替换分类头（与训练时一致）
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.5),  # 防止过拟合
            nn.Linear(num_ftrs, num_classes)
        )

        return model.to(device)

    except Exception as e:
        print(f"模型初始化失败: {e}")
        exit(1)

# 预测单张图片
def predict_single_image(model, image_path, class_names):
    """对指定路径的图片进行分类预测"""
    # 检查文件是否存在
    if not os.path.exists(image_path):
        return None, f"错误：文件不存在 - {image_path}"

    try:
        # 打开并预处理图片
        image = Image.open(image_path).convert('RGB')
        original_image = image.copy()  # 保存原始图像用于显示

        # 应用预处理
        transformed_image = data_transforms['test'](image)
        image_tensor = transformed_image.unsqueeze(0).to(device)

        # 模型预测
        model.eval()
        with torch.no_grad():
            outputs = model(image_tensor)
            probs = torch.softmax(outputs, dim=1)  # 转换为概率分布
            conf, preds = torch.max(probs, 1)  # 获取最高概率及其索引

        # 获取预测结果
        pred_class = class_names[preds.item()]
        confidence = conf.item() * 100

        return original_image, f"预测类别: {pred_class}\n置信度: {confidence:.2f}%"

    except Exception as e:
        return None, f"预测过程出错: {e}"


# 显示预测结果，增加中文字体配置
def show_prediction_result(image, result_text):
    """可视化预测结果，配置中文字体避免乱码"""

    # 配置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决负号显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False

    if image is None:
        print(result_text)  # 打印错误信息
        return

    plt.figure(figsize=(8, 6))
    plt.imshow(image)
    plt.axis('off')
    plt.title(result_text, fontsize=14)
    plt.tight_layout()
    plt.show()


# 主程序
if __name__ == '__main__':
    print("===== 图像分类预测系统 =====")
    print(f"支持类别: {', '.join(class_names)}")

    # 初始化模型
    print("\n正在初始化模型...")
    model = initialize_model(len(class_names))

    # 加载预训练权重
    if os.path.exists(weight_path):
        print(f"加载模型权重: {weight_path}")
        try:
            checkpoint = torch.load(weight_path, map_location=device)
            model.load_state_dict(checkpoint['state_dict'])
            print("模型加载成功!")
        except Exception as e:
            print(f"权重加载失败: {e}")
            exit(1)
    else:
        print(f"错误：权重文件不存在 - {weight_path}")
        exit(1)

    # 获取用户输入的图片路径
    image_path = input("\n请输入图片路径: ").strip()

    # 进行预测
    image, result = predict_single_image(model, image_path, class_names)

    # 显示结果
    show_prediction_result(image, result)
    print("\n===== 预测完成 =====")