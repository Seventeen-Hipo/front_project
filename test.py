from config import device
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import torch


def test_model(model, dataloaders, dataset_sizes, class_names, criterion):
    """测试集评估（含多种评估指标和混淆矩阵）"""
    # 关闭Dropout和BatchNorm等训练专用层
    model.eval()
    # 累积测试损失
    test_loss = 0
    # 正确预测总数
    correct = 0

    # 用于收集所有预测和真实标签
    # 存储所有预测的结果
    all_preds = []
    # 存储所有的真实标签
    all_labels = []

    # 类别级统计
    # 每个类别的正确数
    class_correct = list(0. for _ in range(len(class_names)))
    # 每个类别的总数
    class_total = list(0. for _ in range(len(class_names)))

    # 禁用梯度计算
    with torch.no_grad():
        for inputs, labels in dataloaders['test']:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            test_loss += loss.item() * inputs.size(0)

            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data)

            # 收集预测和标签
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

            # 统计类别级准确率
            c = (preds == labels).squeeze()
            for i in range(len(labels)):
                label = labels[i]
                class_correct[label] += c[i].item()
                class_total[label] += 1

    # 计算整体与类别级指标
    test_loss /= dataset_sizes['test']
    test_acc = correct.double() / dataset_sizes['test']

    print(f'\nTest Loss: {test_loss:.4f}')
    print(f'Test Accuracy: {test_acc:.4f} ({correct}/{dataset_sizes["test"]})')

    # 计算并打印分类报告（精确率、召回率、F1值）
    print("\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=class_names, digits=4))

    # 计算并绘制混淆矩阵
    cm = confusion_matrix(all_labels, all_preds)
    plot_confusion_matrix(cm, class_names, title='Confusion Matrix')

    # 打印类别级准确率
    print("\nClass-wise Accuracy:")
    for i, class_name in enumerate(class_names):
        if class_total[i] > 0:
            acc = 100 * class_correct[i] / class_total[i]
            print(f'Accuracy of {class_name:<10}: {acc:.2f}%')
        else:
            print(f'Accuracy of {class_name}: N/A')

    return test_loss, test_acc


def plot_confusion_matrix(cm, class_names, title='Confusion Matrix', cmap=plt.cm.Blues):
    """绘制混淆矩阵"""
    plt.figure(figsize=(12, 10))

    # 归一化混淆矩阵
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    # 使用 Seaborn 绘制热力图
    sns.heatmap(cm_normalized, annot=True, fmt=".2f", cmap=cmap,
                xticklabels=class_names, yticklabels=class_names)

    plt.title(title)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.show()