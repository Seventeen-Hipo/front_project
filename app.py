from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import hashlib
import re
import os
import io

# 初始化FastAPI应用
app = FastAPI(title="动物科普网")
# --------------------------
# ML 模型初始化（懒加载，避免导入失败导致 ASGI 无法启动）
# --------------------------
_model = None
class_names = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']
weight_path = 'cifar10_best.pt'
device = None
data_transforms = None

def _ensure_model_loaded():
    global _model, device, data_transforms
    if _model is not None:
        return True
    try:
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        import torch
        from torch import nn
        from torchvision import models
        from torchvision.models import ResNet18_Weights
        from torchvision import transforms
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        data_transforms = {
            'test': transforms.Compose([
                transforms.Resize((32, 32)),
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
            ])
        }
        def initialize_model(num_classes):
            model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
            for p in model.parameters():
                p.requires_grad = False
            num_ftrs = model.fc.in_features
            model.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(num_ftrs, num_classes))
            return model.to(device)
        _loc_model = initialize_model(len(class_names))
        import os as _os
        import torch as _torch
        if _os.path.exists(weight_path):
            checkpoint = _torch.load(weight_path, map_location=device)
            _loc_model.load_state_dict(checkpoint['state_dict'])
            _loc_model.eval()
        _model = _loc_model
        return True
    except Exception as e:
        print(f"模型加载失败或未安装依赖: {e}")
        _model = None
        return False

# 配置CORS，允许前端请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件（CSS, JS, 图片等）
from fastapi.responses import FileResponse

# 模板目录（已不使用模板，保留占位）
templates = None

def get_current_user(request: Request):
    username = request.cookies.get("session_user")
    user_id = request.cookies.get("session_user_id")
    if username and user_id:
        return {"id": user_id, "username": username}
    return None

# --------------------------
# MySQL数据库连接配置
# --------------------------
def get_db_connection():
    """获取MySQL数据库连接"""
    try:
        conn = pymysql.connect(
            host="localhost",    # 本地数据库地址
            user="root",         # 用户名
            password="123456",  # 替换为你的MySQL实际密码
            database="user_system",  # 数据库名
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"数据库连接错误: {e}")
        raise

# --------------------------
# 工具函数
# --------------------------
def hash_password(password: str) -> str:
    """密码加密（SHA256）"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$'
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    """验证用户名格式（3-15位字母数字）"""
    pattern = r'^[a-zA-Z0-9]{3,15}$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> bool:
    """验证密码格式（6-20位）"""
    return 6 <= len(password) <= 20

# --------------------------
# 页面路由
# --------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("home.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/home", response_class=HTMLResponse)
async def home():
    with open("home.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/login", response_class=HTMLResponse)
async def show_login(error: str = None, success: str = None, next: str = None):
    with open("login.html", "r", encoding="utf-8") as f:
        content = f.read()
        if error:
            content = content.replace('id="errorMessage"', 'id="errorMessage" style="display: block;"').replace('{{error}}', error)
        if success:
            content = content.replace('id="errorMessage"', 'id="errorMessage" style="display: block;"').replace('{{success}}', success)
        if next:
            # 在表单中注入隐藏域（若页面无隐藏域，则简单附加提示）
            content = content.replace('</form>', f'\n<input type="hidden" name="next" value="{next}">\n</form>')
        return HTMLResponse(content=content)

@app.get("/register", response_class=HTMLResponse)
async def show_register(error: str = None, success: str = None):
    with open("register.html", "r", encoding="utf-8") as f:
        content = f.read()
        if error:
            content = content.replace('id="errorMessage"', 'id="errorMessage" style="display: block;"').replace('{{error}}', error)
        if success:
            content = content.replace('id="errorMessage"', 'id="errorMessage" style="display: block;"').replace('{{success}}', success)
        return HTMLResponse(content=content)

# --------------------------
# favicon 避免 404
# --------------------------
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# --------------------------
# 页面：动物识别（需登录）
# --------------------------
@app.get("/identify", response_class=HTMLResponse)
async def identify_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=请先登录后再访问动物识别功能&next=%2Fidentify", status_code=303)
    # 返回独立页面文件
    with open("identify.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# --------------------------
# 预测接口（需登录）
# --------------------------
from fastapi import UploadFile, File as UploadFileField

@app.post("/api/predict")
async def api_predict(request: Request, file: UploadFile = UploadFileField(...)):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "未登录"})
    if not _ensure_model_loaded():
        return JSONResponse(status_code=503, content={"detail": "模型未就绪或依赖未安装"})

    try:
        contents = await file.read()
        from PIL import Image as _Image
        import torch as _torch
        image = _Image.open(io.BytesIO(contents)).convert('RGB')
        transformed_image = data_transforms['test'](image)
        image_tensor = transformed_image.unsqueeze(0).to(device)
        with _torch.no_grad():
            outputs = _model(image_tensor)
            probs = _torch.softmax(outputs, dim=1)
            conf, preds = _torch.max(probs, 1)
        pred_class = class_names[preds.item()]
        confidence = float(round(conf.item() * 100, 2))
        return {
            "predicted_class": pred_class,
            "confidence": confidence,
            "message": "预测成功"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"预测过程出错: {str(e)}"})

# --------------------------
# API路由 - 登录验证
# --------------------------
@app.post("/api/login")
async def api_login(username: str = Form(...), password: str = Form(...)):
    """登录API - 返回JSON格式"""
    conn = None
    cursor = None
    
    try:
        # 验证输入
        if not validate_username(username):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "用户名格式错误，需3-15位字母或数字"}
            )
        
        if not validate_password(password):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "密码格式错误，需6-20位字符"}
            )
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先按哈希密码校验
        sql_hashed = "SELECT id, username FROM users WHERE username = %s AND password = %s"
        hashed_password = hash_password(password)
        cursor.execute(sql_hashed, (username, hashed_password))
        user = cursor.fetchone()

        # 如果未找到，再按明文密码兼容老数据；若命中则升级为哈希存储
        if not user:
            sql_plain = "SELECT id, username FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql_plain, (username, password))
            user_plain = cursor.fetchone()
            if user_plain:
                # 升级该用户密码为哈希
                try:
                    update_sql = "UPDATE users SET password = %s WHERE id = %s"
                    cursor.execute(update_sql, (hashed_password, user_plain["id"]))
                    conn.commit()
                except Exception:
                    # 升级失败不影响当前登录
                    conn.rollback()
                user = user_plain
        
        if user:
            response = JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "登录成功",
                    "user": {
                        "id": user["id"],
                        "username": user["username"]
                    }
                }
            )
            response.set_cookie(key="session_user", value=user["username"], httponly=True)
            response.set_cookie(key="session_user_id", value=str(user["id"]), httponly=True)
            return response
        else:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "用户名或密码错误"}
            )
    
    except Exception as e:
        print(f"登录错误: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"服务器错误: {str(e)}"}
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------
# API路由 - 注册
# --------------------------
@app.post("/api/register")
async def api_register(
    username: str = Form(...),
    password: str = Form(...)
):
    """注册API - 返回JSON格式"""
    conn = None
    cursor = None
    
    try:
        # 验证输入格式
        if not validate_username(username):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "用户名格式错误，需3-15位字母或数字"}
            )
        
        if not validate_password(password):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "密码格式错误，需6-20位字符"}
            )
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        check_sql = "SELECT id FROM users WHERE username = %s"
        cursor.execute(check_sql, (username,))
        if cursor.fetchone():
            return JSONResponse(
                status_code=409,
                content={"success": False, "message": "用户名已存在"}
            )
        
        # 插入新用户（密码加密存储）
        hashed_password = hash_password(password)
        insert_sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(insert_sql, (username, hashed_password))
        conn.commit()
        
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "注册成功，请登录"}
        )
    
    except pymysql.err.IntegrityError as e:
        return JSONResponse(
            status_code=409,
            content={"success": False, "message": "用户名已存在"}
        )
    except Exception as e:
        print(f"注册错误: {e}")
        if conn:
            conn.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"服务器错误: {str(e)}"}
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------
# 传统表单提交路由（兼容性）
# --------------------------
@app.post("/login")
async def handle_login(username: str = Form(...), password: str = Form(...), next: str = Form(None)):
    """传统表单提交登录"""
    result = await api_login(username, password)
    if result.status_code == 200:
        redirect_to = next if next else "/home"
        resp = RedirectResponse(url=redirect_to, status_code=303)
        # 设置 Cookie
        try:
            conn = get_db_connection(); c2 = conn.cursor()
            c2.execute("SELECT id FROM users WHERE username=%s", (username,))
            got = c2.fetchone(); c2.close(); conn.close()
            if got:
                resp.set_cookie(key="session_user", value=username, httponly=True)
                resp.set_cookie(key="session_user_id", value=str(got["id"]), httponly=True)
        except Exception:
            pass
        return resp
    else:
        error_msg = "用户名或密码错误"
        return RedirectResponse(url=f"/login?error={error_msg}", status_code=303)

@app.post("/register")
async def handle_register(
    username: str = Form(...),
    password: str = Form(...)
):
    """传统表单提交注册"""
    result = await api_register(username, password)
    if result.status_code == 200:
        return RedirectResponse(url="/login?success=注册成功，请登录", status_code=303)
    else:
        error_msg = "注册失败"
        return RedirectResponse(url=f"/register?error={error_msg}", status_code=303)

# --------------------------
# 登出
# --------------------------
@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/")
    resp.delete_cookie("session_user")
    resp.delete_cookie("session_user_id")
    return resp

# --------------------------
# 当前登录用户信息
# --------------------------
@app.get("/api/me")
async def api_me(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"success": False, "message": "未登录"})
    return {"success": True, "user": user}

# --------------------------
# 静态文件服务（放在最后，避免路由冲突）
# --------------------------
@app.get("/{filepath:path}")
async def serve_static(filepath: str):
    """提供静态文件服务（CSS, JS, 图片等）"""
    # 只允许特定文件类型
    allowed_extensions = ['.html', '.css', '.js', '.jpg', '.jpeg', '.png', '.webp', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']
    if any(filepath.endswith(ext) for ext in allowed_extensions):
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return FileResponse(filepath)
    
    # 如果不是静态文件，返回404
    return JSONResponse(status_code=404, content={"detail": "Not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

