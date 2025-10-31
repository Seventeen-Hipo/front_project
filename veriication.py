from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pymysql
from passlib.context import CryptContext
from pymysql.cursors import DictCursor

# 1. 初始化 FastAPI 应用
app = FastAPI()

# 2. 配置模板和静态文件（与 Flask 的 templates/static 目录结构一致）
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 4. 数据库连接配置（替换为你的数据库信息）
def get_db_connection():
    conn = pymysql.connect(
        host='localhost',        # 数据库地址
        user='root',             # 用户名
        password='123456',       # 密码（有则填写）
        db='user_system',        # 数据库名（需提前创建）
        charset='utf8mb4',
        cursorclass=DictCursor   # 结果以字典形式返回
    )
    return conn

# 5. 路由1：显示注册页面（GET 请求）
@app.get("/", response_class=HTMLResponse)
def show_register(request: Request):
    # 传递 flash 消息（FastAPI 无内置 flash，用查询参数模拟）
    message = request.query_params.get("message", "")
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "message": message}
    )

# 6. 路由2：处理注册提交（POST 请求）
@app.post("/register", response_class=RedirectResponse)
def handle_register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...)
):
    # 清理输入（去除首尾空格）
    username = username.strip()
    password = password.strip()
    email = email.strip()

    # 后端数据验证
    if len(username) < 3 or len(username) > 15:
        return RedirectResponse(
            url="/?message=用户名需3-15位字符！",
            status_code=status.HTTP_303_SEE_OTHER
        )
    if len(password) < 6 or len(password) > 20:
        return RedirectResponse(
            url="/?message=密码需6-20位字符！",
            status_code=status.HTTP_303_SEE_OTHER
        )
    if "@" not in email or "." not in email.split("@")[-1]:
        return RedirectResponse(
            url="/?message=请输入正确的邮箱格式！",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 加密密码
    hashed_password = pwd_context.hash(password)

    # 数据库操作
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 参数化查询防止 SQL 注入
            sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, email))
        conn.commit()
        return RedirectResponse(
            url="/?message=注册成功！可前往登录页",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except pymysql.IntegrityError:
        # 处理用户名/邮箱重复（需数据库表中设置唯一约束）
        return RedirectResponse(
            url="/?message=用户名或邮箱已被注册！",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/?message=注册失败：{str(e)}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    finally:
        if conn:
            conn.close()