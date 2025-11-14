import matplotlib.pyplot as plt
import torch

def plot_training_metrics(val_acc, train_acc, val_loss, train_loss):
    """绘制训练曲线（准确率 + 损失）"""
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))

    # 准确率曲线
    axs[0].plot(range(1, len(train_acc) + 1), train_acc, label='Train Acc')
    axs[0].plot(range(1, len(val_acc) + 1), val_acc, label='Valid Acc')
    axs[0].set_title('Training vs Validation Accuracy')
    axs[0].set_xlabel('Epochs')
    axs[0].set_ylabel('Accuracy')
    axs[0].legend()
    axs[0].grid(True, linestyle='--', alpha=0.7)

    # 损失曲线
    axs[1].plot(range(1, len(train_loss) + 1), train_loss, label='Train Loss')
    axs[1].plot(range(1, len(val_loss) + 1), val_loss, label='Valid Loss')
    axs[1].set_title('Training vs Validation Loss')
    axs[1].set_xlabel('Epochs')
    axs[1].set_ylabel('Loss')
    axs[1].legend()
    axs[1].grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('training_metrics.png')
    plt.show()


def print_device_info():
    """打印设备信息"""
    print('CUDA is available, Training on GPU...'
          if torch.cuda.is_available()
          else 'CUDA is not available, Training on CPU...')


def plot_class_accuracy(class_names, class_correct, class_total):
    """绘制类别级准确率柱状图"""
    plt.figure(figsize=(12, 6))

    # 计算准确率百分比
    accuracies = [100 * class_correct[i] / class_total[i] for i in range(len(class_names))]

    # 创建柱状图
    plt.bar(class_names, accuracies, color='skyblue')

    # 添加数值标签
    for i, acc in enumerate(accuracies):
        plt.text(i, acc + 0.5, f'{acc:.1f}%', ha='center')

    plt.title('Class-wise Accuracy')
    plt.xlabel('Class')
    plt.ylabel('Accuracy (%)')
    plt.ylim(0, 110)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('class_accuracy.png')
    plt.show()