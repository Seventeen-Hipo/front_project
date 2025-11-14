# 动物科普网 API 使用说明

## 项目结构

```
front_project/
├── app.py                 # FastAPI后端服务器（主文件）
├── connect_database.py    # 原始数据库连接文件（参考）
├── init_database.py       # 数据库初始化脚本
├── requirements.txt       # Python依赖包
├── home.html             # 主页面
├── login.html            # 登录页面
├── register.html         # 注册页面
├── login_style.css       # 登录页面样式
├── register_style.css    # 注册页面样式
└── home_style.css        # 主页面样式
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `app.py` 中的数据库配置：

```python
def get_db_connection():
    conn = pymysql.connect(
        host="localhost",      # 数据库地址
        user="root",           # 用户名
        password="123456",     # 修改为你的MySQL密码
        database="user_system", # 数据库名
        charset="utf8mb4"
    )
    return conn
```

### 3. 初始化数据库

```bash
python init_database.py
```

这将创建：
- 数据库：`user_system`
- 表：`users`
- 可选：创建测试用户

### 4. 启动服务器

```bash
# 方法1：使用uvicorn
uvicorn app:app --reload

# 方法2：直接运行
python app.py
```

服务器将在 `http://localhost:8000` 启动

## API 接口

### 1. 登录接口

**POST** `/api/login`

请求参数（Form Data）：
- `username`: 用户名（3-15位字母数字）
- `password`: 密码（6-20位）

响应示例：
```json
{
    "success": true,
    "message": "登录成功",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    }
}
```

### 2. 注册接口

**POST** `/api/register`

请求参数（Form Data）：
- `username`: 用户名（3-15位字母数字）
- `password`: 密码（6-20位）
- `email`: 邮箱（有效格式）

响应示例：
```json
{
    "success": true,
    "message": "注册成功，请登录"
}
```

### 3. 页面路由

- `GET /` - 首页
- `GET /home` - 主页
- `GET /login` - 登录页面
- `GET /register` - 注册页面
- `POST /login` - 传统表单提交登录（兼容性）
- `POST /register` - 传统表单提交注册（兼容性）

## 前端使用

### 登录页面（login.html）

登录表单使用 AJAX 提交：

```javascript
// 自动处理，无需额外代码
// 表单提交到 /api/login
// 成功后跳转到 /home
```

### 注册页面（register.html）

注册表单使用 AJAX 提交：

```javascript
// 自动处理，无需额外代码
// 表单提交到 /api/register
// 成功后跳转到 /login
```

## 安全说明

1. **密码加密**：使用 SHA256 加密存储密码
2. **输入验证**：前后端双重验证
3. **SQL注入防护**：使用参数化查询
4. **错误处理**：统一的错误响应格式

## 数据库结构

### users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(15) | 用户名，唯一 |
| password | VARCHAR(64) | 密码（SHA256加密） |
| email | VARCHAR(100) | 邮箱，唯一 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## 常见问题

### 1. 数据库连接失败

- 检查MySQL服务是否启动
- 确认数据库配置正确（用户名、密码）
- 确认数据库已创建

### 2. 端口被占用

修改 `app.py` 最后的端口配置：
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # 修改端口
```

### 3. CORS 错误

如果前后端不在同一端口，需要配置 CORS：
```python
# app.py 中已配置允许所有来源
# 生产环境建议限制为特定域名
```

## 开发建议

1. **密码加密**：生产环境建议使用 bcrypt 等更安全的加密方式
2. **Session管理**：建议添加 JWT 或 Session 管理
3. **日志记录**：添加操作日志和错误日志
4. **API文档**：访问 `http://localhost:8000/docs` 查看自动生成的API文档

