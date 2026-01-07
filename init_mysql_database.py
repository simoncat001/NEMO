#!/usr/bin/env python3
"""
MySQL数据库初始化脚本
根据PostgreSQL schema转换为MySQL
"""

import mysql.connector
from mysql.connector import Error
import sys

# MySQL连接配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'port': 3306
}

DB_NAME = 'nemo_db'

def create_database():
    """创建数据库"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        print(f"正在创建数据库 {DB_NAME}...")
        
        # 删除已存在的数据库（如果存在）
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        print(f"已删除旧数据库（如果存在）")
        
        # 创建新数据库
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {DB_NAME} 创建成功！")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"错误: {e}")
        return False

def create_tables():
    """创建基础表结构"""
    try:
        # 连接到新创建的数据库
        config = MYSQL_CONFIG.copy()
        config['database'] = DB_NAME
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("\n正在创建表结构...")
        
        # 创建表的SQL语句（从PostgreSQL转换为MySQL格式）
        tables = [
            # account表
            """
            CREATE TABLE account (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                start_date DATE,
                type_id INT,
                note TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # account_type表
            """
            CREATE TABLE account_type (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                display_order INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # activityhistory表
            """
            CREATE TABLE activityhistory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                object_id INT NOT NULL CHECK (object_id >= 0),
                action BOOLEAN NOT NULL,
                date DATETIME NOT NULL,
                authorizer_id INT NOT NULL,
                content_type_id INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # adjustment_request表
            """
            CREATE TABLE adjustment_request (
                id INT AUTO_INCREMENT PRIMARY KEY,
                creation_time DATETIME NOT NULL,
                last_updated DATETIME NOT NULL,
                item_id INT CHECK (item_id >= 0),
                description TEXT,
                manager_note TEXT,
                new_start DATETIME,
                new_end DATETIME,
                status INT NOT NULL,
                deleted BOOLEAN NOT NULL DEFAULT FALSE,
                creator_id INT NOT NULL,
                item_type_id INT,
                last_updated_by_id INT,
                reviewer_id INT,
                applied BOOLEAN NOT NULL DEFAULT FALSE,
                applied_by_id INT,
                new_quantity INT CHECK (new_quantity >= 0),
                waive BOOLEAN NOT NULL DEFAULT FALSE,
                new_project_id INT,
                original_end DATETIME,
                original_project_id INT,
                original_quantity INT CHECK (original_quantity >= 0),
                original_start DATETIME,
                item_area_id INT,
                item_tool_id INT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # alert表
            """
            CREATE TABLE alert (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                contents TEXT NOT NULL,
                creation_time DATETIME NOT NULL,
                debut_time DATETIME NOT NULL,
                expiration_time DATETIME,
                dismissible BOOLEAN NOT NULL DEFAULT TRUE,
                creator_id INT,
                user_id INT,
                category VARCHAR(255) NOT NULL,
                deleted BOOLEAN NOT NULL DEFAULT FALSE,
                expired BOOLEAN NOT NULL DEFAULT FALSE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # user表（简化版）
            """
            CREATE TABLE user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # tool表
            """
            CREATE TABLE tool (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                visible BOOLEAN NOT NULL DEFAULT TRUE,
                operational BOOLEAN NOT NULL DEFAULT TRUE,
                category VARCHAR(100),
                location VARCHAR(200)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # project表
            """
            CREATE TABLE project (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                application_identifier VARCHAR(255),
                active BOOLEAN NOT NULL DEFAULT TRUE,
                start_date DATE,
                account_id INT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # area表
            """
            CREATE TABLE area (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                requires_reservation BOOLEAN NOT NULL DEFAULT FALSE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # reservation表
            """
            CREATE TABLE reservation (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                creator_id INT NOT NULL,
                tool_id INT,
                area_id INT,
                project_id INT,
                start DATETIME NOT NULL,
                end DATETIME NOT NULL,
                cancelled BOOLEAN NOT NULL DEFAULT FALSE,
                missed BOOLEAN NOT NULL DEFAULT FALSE,
                short_notice BOOLEAN NOT NULL DEFAULT FALSE,
                creation_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # usage_event表
            """
            CREATE TABLE usage_event (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                operator_id INT NOT NULL,
                tool_id INT,
                project_id INT,
                start DATETIME NOT NULL,
                end DATETIME,
                run_data TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            # consumable表
            """
            CREATE TABLE consumable (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL DEFAULT 0,
                category VARCHAR(100),
                visible BOOLEAN NOT NULL DEFAULT TRUE,
                reminder_threshold INT,
                reminder_email VARCHAR(255)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
        ]
        
        for i, table_sql in enumerate(tables, 1):
            try:
                cursor.execute(table_sql)
                print(f"  [{i}/{len(tables)}] 表创建成功")
            except Error as e:
                print(f"  [{i}/{len(tables)}] 表创建失败: {e}")
        
        connection.commit()
        print(f"\n表结构创建完成！")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"错误: {e}")
        return False

def create_admin_user():
    """创建管理员用户"""
    try:
        config = MYSQL_CONFIG.copy()
        config['database'] = DB_NAME
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("\n正在创建管理员用户...")
        
        # 简单的密码哈希（实际应用中应该使用bcrypt等）
        from datetime import datetime
        
        insert_sql = """
        INSERT INTO user (username, password, email, first_name, last_name, 
                         is_active, is_staff, is_superuser, date_joined)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        admin_data = (
            'admin',
            'admin',  # 密码应该在实际使用时加密
            'admin@nemo.local',
            'Admin',
            'User',
            True,
            True,
            True,
            datetime.now()
        )
        
        cursor.execute(insert_sql, admin_data)
        connection.commit()
        
        print("管理员用户创建成功！")
        print("  用户名: admin")
        print("  密码: admin")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("NEMO MySQL 数据库初始化")
    print("=" * 60)
    print(f"MySQL 配置:")
    print(f"  主机: {MYSQL_CONFIG['host']}")
    print(f"  端口: {MYSQL_CONFIG['port']}")
    print(f"  用户: {MYSQL_CONFIG['user']}")
    print(f"  数据库: {DB_NAME}")
    print("=" * 60)
    
    # 步骤1: 创建数据库
    if not create_database():
        print("\n数据库创建失败！")
        sys.exit(1)
    
    # 步骤2: 创建表
    if not create_tables():
        print("\n表结构创建失败！")
        sys.exit(1)
    
    # 步骤3: 创建管理员用户
    if not create_admin_user():
        print("\n管理员用户创建失败！")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("数据库初始化完成！")
    print("=" * 60)
    print("\n你现在可以启动后端服务了：")
    print("  cd backend")
    print("  pip install -r requirements.txt")
    print("  uvicorn main:app --reload")
    print("\n数据库连接字符串：")
    print(f"  mysql+aiomysql://root:12345678@localhost:3306/{DB_NAME}")
    print("=" * 60)

if __name__ == "__main__":
    main()
