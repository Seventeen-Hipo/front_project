import os
import torch
from torch import nn
from torchvision import models
from torchvision.models import ResNet18_Weights
from PIL import Image
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from torchvision import transforms

# 解决OpenMP冲突
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 初始化FastAPI应用
app = FastAPI(title="CIFAR-10图像分类API", description="基于ResNet18的CIFAR-10图像分类服务")

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
weight_path = 'cifar10_best.pt'
class_names = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']


# 初始化模型并加载权重（只在服务启动时执行一次）
def initialize_model(num_classes):
    try:
        model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

        # 冻结参数
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
        raise


# 加载模型
try:
    print("初始化模型...")
    model = initialize_model(len(class_names))

    if os.path.exists(weight_path):
        print(f"加载模型权重: {weight_path}")
        checkpoint = torch.load(weight_path, map_location=device)
        model.load_state_dict(checkpoint['state_dict'])
        model.eval()  # 设置为评估模式
        print("模型加载成功!")
    else:
        raise Exception(f"权重文件不存在: {weight_path}")
except Exception as e:
    print(f"模型加载失败: {e}")
    raise


# 定义响应模型
class PredictionResult(BaseModel):
    predicted_class: str
    confidence: float
    message: str


# 根路径
@app.get("/")
def read_root():
    return {
        "message": "CIFAR-10图像分类API服务已启动",
        "支持类别": class_names,
        "使用方法": "发送POST请求到/predict接口，上传图片文件"
    }


# 预测接口
@app.post("/predict", response_model=PredictionResult)
async def predict_image(file: UploadFile = File(...)):
    """接收上传的图片文件，返回分类预测结果"""
    try:
        # 验证文件类型
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            raise HTTPException(status_code=400, detail="请上传图片文件（支持png, jpg, jpeg, bmp, gif格式）")

        # 读取图片内容
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')

        # 预处理
        transformed_image = data_transforms['test'](image)
        image_tensor = transformed_image.unsqueeze(0).to(device)

        # 模型预测
        with torch.no_grad():
            outputs = model(image_tensor)
            probs = torch.softmax(outputs, dim=1)
            conf, preds = torch.max(probs, 1)

        # 整理结果
        pred_class = class_names[preds.item()]
        confidence = float(conf.item() * 100)

        return {
            "predicted_class": pred_class,
            "confidence": round(confidence, 2),
            "message": "预测成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测过程出错: {str(e)}")


# 健康检查接口
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "device": str(device),
        "model_loaded": True
    }