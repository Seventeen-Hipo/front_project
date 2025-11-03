from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import hashlib
import re

# 初始化FastAPI应用
app = FastAPI(title="动物科普网")

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
import os

# 配置模板目录（如果使用模板）
try:
    templates = Jinja2Templates(directory=".")
except:
    templates = None

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
    """首页"""
    with open("home.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/home", response_class=HTMLResponse)
async def home():
    """主页"""
    with open("home.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/login", response_class=HTMLResponse)
async def show_login(error: str = None):
    """登录页面"""
    with open("login.html", "r", encoding="utf-8") as f:
        content = f.read()
        # 如果有错误信息，注入到页面中
        if error:
            content = content.replace('id="errorMessage"', f'id="errorMessage" style="display: block;"')
            content = content.replace('{{error}}', error)
        return HTMLResponse(content=content)

@app.get("/register", response_class=HTMLResponse)
async def show_register(error: str = None):
    """注册页面"""
    with open("register.html", "r", encoding="utf-8") as f:
        content = f.read()
        # 如果有错误信息，注入到页面中
        if error:
            content = content.replace('id="errorMessage"', f'id="errorMessage" style="display: block;"')
            content = content.replace('{{error}}', error)
        return HTMLResponse(content=content)

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
        
        # 查询用户（密码已加密存储时使用hash_password(password)）
        sql = "SELECT id, username, email FROM users WHERE username = %s AND password = %s"
        hashed_password = hash_password(password)
        cursor.execute(sql, (username, hashed_password))
        user = cursor.fetchone()
        
        if user:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "登录成功",
                    "user": {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user.get("email", "")
                    }
                }
            )
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
    password: str = Form(...),
    email: str = Form(...)
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
        
        if not validate_email(email):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "邮箱格式错误"}
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
        
        # 检查邮箱是否已存在
        check_sql = "SELECT id FROM users WHERE email = %s"
        cursor.execute(check_sql, (email,))
        if cursor.fetchone():
            return JSONResponse(
                status_code=409,
                content={"success": False, "message": "邮箱已被注册"}
            )
        
        # 插入新用户（密码加密存储）
        hashed_password = hash_password(password)
        insert_sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (username, hashed_password, email))
        conn.commit()
        
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "注册成功，请登录"}
        )
    
    except pymysql.err.IntegrityError as e:
        return JSONResponse(
            status_code=409,
            content={"success": False, "message": "用户名或邮箱已存在"}
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
async def handle_login(username: str = Form(...), password: str = Form(...)):
    """传统表单提交登录"""
    result = await api_login(username, password)
    if result.status_code == 200:
        return RedirectResponse(url="/home", status_code=303)
    else:
        error_msg = "用户名或密码错误"
        return RedirectResponse(url=f"/login?error={error_msg}", status_code=303)

@app.post("/register")
async def handle_register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...)
):
    """传统表单提交注册"""
    result = await api_register(username, password, email)
    if result.status_code == 200:
        return RedirectResponse(url="/login?success=注册成功，请登录", status_code=303)
    else:
        error_msg = "注册失败"
        return RedirectResponse(url=f"/register?error={error_msg}", status_code=303)

# --------------------------
# 静态文件服务（放在最后，避免路由冲突）
# --------------------------
@app.get("/{filepath:path}")
async def serve_static(filepath: str):
    """提供静态文件服务（CSS, JS, 图片等）"""
    # 只允许特定文件类型
    allowed_extensions = ['.css', '.js', '.jpg', '.jpeg', '.png', '.webp', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']
    if any(filepath.endswith(ext) for ext in allowed_extensions):
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return FileResponse(filepath)
    
    # 如果不是静态文件，返回404
    return JSONResponse(status_code=404, content={"detail": "Not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

