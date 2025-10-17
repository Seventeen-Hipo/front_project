import os
import warnings
import torch.optim as optim
from torch import nn
from config import set_seed, device, seed, num_epochs_phase1, num_epochs_phase2
from config import learning_rate_phase1, learning_rate_phase2
from data_loader import load_datasets
from model import initialize_model
from train import train_model
from test import test_model
from utils import plot_training_metrics, print_device_info

# 忽略警告
warnings.filterwarnings('ignore')
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if __name__ == '__main__':
    # 设置随机种子
    set_seed(seed)

    # 打印设备信息
    print_device_info()

    # 1. 加载数据集
    print("Loading datasets...")
    dataloaders, dataset_sizes, class_names = load_datasets()
    print(f"Classes: {class_names}")

    # 2. 初始化模型（ResNet18 + 冻结预训练层）
    print("Initializing model...")
    model = initialize_model(
        model_name='resnet18',
        num_classes=len(class_names),
        feature_extract=True
    )

    # 定义损失函数
    criterion = nn.CrossEntropyLoss()

    # 3. 第一阶段训练：冻结预训练层，训练分类头
    print("\nPhase 1: 冻结预训练层，训练分类头")
    optimizer_phase1 = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),  # 仅训练可更新参数
        lr=learning_rate_phase1
    )
    scheduler_phase1 = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer_phase1, mode='min', factor=0.5, patience=3
    )

    model, val_acc_phase1, train_acc_phase1, val_loss_phase1, train_loss_phase1 = train_model(
        model, dataloaders, dataset_sizes, criterion,
        optimizer_phase1, scheduler_phase1, num_epochs=num_epochs_phase1
    )

    # 4. 第二阶段训练：解冻所有层，微调整个网络
    print("\nPhase 2: 解冻所有层，微调整个网络")
    for param in model.parameters():
        param.requires_grad = True  # 解冻所有层

    optimizer_phase2 = optim.Adam(
        model.parameters(),
        lr=learning_rate_phase2  # 降低学习率
    )
    scheduler_phase2 = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer_phase2, mode='min', factor=0.5, patience=3
    )

    # 继续训练
    model, val_acc_phase2, train_acc_phase2, val_loss_phase2, train_loss_phase2 = train_model(
        model, dataloaders, dataset_sizes, criterion,
        optimizer_phase2, scheduler_phase2, num_epochs=num_epochs_phase2
    )

    # 合并训练曲线
    val_acc_history = val_acc_phase1 + val_acc_phase2
    train_acc_history = train_acc_phase1 + train_acc_phase2
    valid_losses = val_loss_phase1 + val_loss_phase2
    train_losses = train_loss_phase1 + train_loss_phase2

    # 5. 测试集评估
    print("\nEvaluating on test set...")
    test_loss, test_acc = test_model(model, dataloaders, dataset_sizes, class_names, criterion)

    # 6. 可视化训练曲线
    print("\nPlotting training metrics...")
    plot_training_metrics(val_acc_history, train_acc_history, valid_losses, train_losses)

    print("\nAll tasks completed!")