from torch import nn
from torchvision import models
from config import device

def set_parameter_requires_grad(model, feature_extracting):
    """控制模型参数是否参与训练"""
    if feature_extracting:
        for param in model.parameters():
            param.requires_grad = False

def initialize_model(model_name, num_classes, feature_extract=True, use_pretrained=True):
    """初始化 ResNet18 模型并修改分类头"""
    if model_name == "resnet18":
        model = models.resnet18(pretrained=use_pretrained)
        # 冻结，不更新参数
        set_parameter_requires_grad(model, feature_extract)

        # 替换分类层（添加 Dropout 防止过拟合）
        # 原始的Resnet18的输入特征数为512，修改为10
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            # 防止过拟合，50%的概率丢掉神经元
            nn.Dropout(0.5),
            # 替换输出的的维度
            nn.Linear(num_ftrs, num_classes))
        model = model.to(device)
        return model
    else:
        print("Invalid model name!")
        exit()