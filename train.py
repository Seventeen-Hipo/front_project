import time
import copy
import torch
from config import filename, device

def train_model(model, dataloaders, dataset_sizes, criterion, optimizer, scheduler, num_epochs=25):
    """完整训练流程（含验证集监控）"""
    # 计算开始时间
    since = time.time()
    # 初始化准确率
    best_acc = 0.0

    # 验证集准确率
    val_acc_history = []
    # 训练集准确率
    train_acc_history = []
    # 训练损失
    train_losses = []
    # 验证损失
    valid_losses = []
    # 初始化最佳模型参数权重
    best_model_wts = copy.deepcopy(model.state_dict())

    for epoch in range(num_epochs):
        print(f'Epoch {epoch + 1}/{num_epochs}')
        print('-' * 10)

        # 训练 + 验证阶段
        for phase in ['train', 'valid']:
            model.train() if phase == 'train' else model.eval()
            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                # 前向传播 + 反向传播（仅训练阶段）
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    # criterion 返回平均损失
                    loss = criterion(outputs, labels)
                    _, preds = torch.max(outputs, 1)

                    if phase == 'train':
                        # 计算损失函数关于所有可训练参数的梯度
                        loss.backward()
                        # 根据梯度更新模型的参数
                        optimizer.step()

                # 统计损失与准确率
                # 损失 = 标量损失值 * 批次大小
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            # 计算 epoch 级指标
            # 平均损失
            epoch_loss = running_loss / dataset_sizes[phase]
            # 准确率
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # 更新最佳模型（仅验证集）
            if phase == 'valid' and epoch_acc > best_acc:
                best_acc = epoch_acc
                # 深拷贝最佳权重参数
                best_model_wts = copy.deepcopy(model.state_dict())
                torch.save({
                    # 权重参数
                    'state_dict': model.state_dict(),
                    # 最佳准确率
                    'best_acc': best_acc,
                    # 优化器状态
                    'optimizer': optimizer.state_dict()
                }, filename)
                print(f'Saved best model (Acc: {best_acc:.4f})')

            # 记录训练曲线数据
            if phase == 'valid':
                val_acc_history.append(epoch_acc.cpu().numpy())
                valid_losses.append(epoch_loss)
            else:
                train_acc_history.append(epoch_acc.cpu().numpy())
                train_losses.append(epoch_loss)

        # 学习率调度（需传入验证集损失）
        # 将验证损失作为输入，指导学习率调整
        if phase == 'valid':
            scheduler.step(epoch_loss)
        print()

    # 训练总结
    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'Best val Acc: {best_acc:.4f}')

    # 加载最佳模型权重
    model.load_state_dict(best_model_wts)
    return model, val_acc_history, train_acc_history, valid_losses, train_losses