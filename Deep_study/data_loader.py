from torchvision import datasets
from Deep_study.config import data_root, get_data_transforms, batch_size
import os
import torch


def load_datasets():
    """加载并划分数据集（训练集、验证集、测试集）"""
    data_transforms = get_data_transforms()

    # 加载训练集
    train_dataset = datasets.ImageFolder(
        root=os.path.join(data_root, 'train'),
        transform=data_transforms['train']
    )

    # 从原始训练集按 8:2 划分训练集与验证集
    train_size = int(0.8 * len(train_dataset))
    valid_size = len(train_dataset) - train_size
    train_dataset, valid_dataset = torch.utils.data.random_split(
        train_dataset, [train_size, valid_size]
    )
    # 修复验证集 transform 赋值
    valid_dataset.dataset.transform = data_transforms['valid']

    # 加载测试集
    test_dataset = datasets.ImageFolder(
        root=os.path.join(data_root, 'test'),
        transform=data_transforms['test']
    )

    # 创建数据加载器
    # 训练集每个epoch的打乱数据的顺序，验证集和测试集不打乱数据的顺序
    # 三个数据集均采用四个子进程传输数据
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
    # 获取类别名
    class_names = train_dataset.dataset.classes
    return dataloaders, dataset_sizes, class_names