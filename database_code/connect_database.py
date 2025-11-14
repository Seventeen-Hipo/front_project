from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pymysql

# 初始化FastAPI应用
app = FastAPI()

# 配置模板目录（指向templates文件夹，读取前端页面）
templates = Jinja2Templates(directory="templates")

# --------------------------
# MySQL数据库连接配置（关键：修改为你的数据库密码）
# --------------------------
def get_db_connection():
    conn = pymysql.connect(
        host="localhost",   
        # 用户名
        user="root",
        # 密码
        password="123456",
        # 数据库名
        database="user_system",
        charset="utf8mb4"
    )
    return conn

# 1. 访问登录页（GET请求，返回适配后的login.html）
@app.get("/login", response_class=HTMLResponse)
async def show_login(request: Request, error: str = None):
    # 传递错误信息到前端（验证失败时触发）
    return templates.TemplateResponse("login.html", {"request": request, "error_msg": error})

# 2. 处理登录提交（POST请求，核心验证逻辑）
@app.post("/login")
async def handle_login(username: str = Form(...), password: str = Form(...)):
    # 连接数据库
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 查询数据库中是否存在匹配的用户名和密码
        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()  # 有匹配数据返回用户信息，无则返回None

        if user:
            # 验证成功：跳转到主页面（/home）
            return RedirectResponse(url="/home", status_code=303)
        else:
            # 验证失败：携带错误信息跳回登录页
            return RedirectResponse(url=f"/login?error=用户名或密码错误", status_code=303)
    finally:
        # 关闭数据库连接，避免资源泄漏
        cursor.close()
        conn.close()

# 3. 主页面（登录成功后跳转）
@app.get("/home", response_class=HTMLResponse)
async def show_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})