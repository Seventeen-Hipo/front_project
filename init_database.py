"""
数据库初始化脚本
用于创建user_system数据库和users表
"""
import pymysql
from pymysql.err import OperationalError

# 数据库配置（请根据实际情况修改）
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',  # 修改为你的MySQL密码
    'charset': 'utf8mb4'
}

# 数据库名和表名
DATABASE_NAME = 'user_system'
TABLE_NAME = 'users'

def create_database():
    """创建数据库"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ 数据库 {DATABASE_NAME} 创建成功")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")
        return False

def create_table():
    """创建用户表"""
    try:
        # 连接到指定数据库
        config = DB_CONFIG.copy()
        config['database'] = DATABASE_NAME
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # 创建users表
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(15) NOT NULL UNIQUE COMMENT '用户名',
            password VARCHAR(64) NOT NULL COMMENT '密码（SHA256加密）',
            email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"✓ 表 {TABLE_NAME} 创建成功")
        
        # 插入测试用户（可选）
        insert_test_user = input("\n是否创建测试用户？(y/n): ").strip().lower()
        if insert_test_user == 'y':
            import hashlib
            
            # 创建测试用户
            test_users = [
                ('admin', '123456', 'admin@example.com'),
                ('test', 'test123', 'test@example.com')
            ]
            
            for username, password, email in test_users:
                # 密码加密
                hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
                
                try:
                    insert_sql = f"INSERT INTO {TABLE_NAME} (username, password, email) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql, (username, hashed_password, email))
                    conn.commit()
                    print(f"✓ 测试用户创建成功: {username} / {password}")
                except pymysql.err.IntegrityError:
                    print(f"⚠ 用户 {username} 已存在，跳过")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("数据库初始化脚本")
    print("=" * 50)
    print(f"\n数据库配置:")
    print(f"  主机: {DB_CONFIG['host']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print(f"  数据库名: {DATABASE_NAME}")
    print(f"  表名: {TABLE_NAME}")
    print("\n开始初始化...\n")
    
    # 创建数据库
    if not create_database():
        return
    
    # 创建表
    if not create_table():
        return
    
    print("\n" + "=" * 50)
    print("✓ 数据库初始化完成！")
    print("=" * 50)
    print("\n现在可以运行以下命令启动服务器:")
    print("  uvicorn app:app --reload")
    print("\n或者直接运行:")
    print("  python app.py")

if __name__ == "__main__":
    main()

