#!/usr/bin/env python
"""
MySQL 数据库初始化脚本
"""
import pymysql
import sys

# MySQL 连接配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'charset': 'utf8mb4'
}

DATABASE_NAME = 'nemo'

def create_database():
    """创建数据库"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        print(f"正在创建数据库 '{DATABASE_NAME}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DATABASE_NAME}")
        cursor.execute(f"CREATE DATABASE {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ 数据库 '{DATABASE_NAME}' 创建成功")
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")
        return False

def create_tables():
    """创建基础表结构"""
    try:
        config = MYSQL_CONFIG.copy()
        config['database'] = DATABASE_NAME
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        print("正在创建表结构...")
        
        # 创建 User 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(150) NOT NULL UNIQUE,
                first_name VARCHAR(150),
                last_name VARCHAR(150),
                email VARCHAR(254),
                is_active BOOLEAN DEFAULT TRUE,
                is_staff BOOLEAN DEFAULT FALSE,
                is_superuser BOOLEAN DEFAULT FALSE,
                date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME NULL,
                password VARCHAR(128) NOT NULL,
                training_required BOOLEAN DEFAULT FALSE,
                physical_access_levels JSON,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ User 表创建成功")
        
        # 创建 Tool 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL UNIQUE,
                category_id INT NULL,
                location VARCHAR(200),
                visible BOOLEAN DEFAULT TRUE,
                operational BOOLEAN DEFAULT TRUE,
                _primary_owner_id INT NULL,
                _backup_owners JSON,
                _requires_area_access_id INT NULL,
                grant_physical_access_level_upon_qualification INT NULL,
                INDEX idx_name (name),
                INDEX idx_visible (visible),
                INDEX idx_operational (operational)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Tool 表创建成功")
        
        # 创建 Project 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL UNIQUE,
                application_identifier VARCHAR(200) UNIQUE,
                active BOOLEAN DEFAULT TRUE,
                account_id INT NULL,
                start_date DATE NULL,
                INDEX idx_name (name),
                INDEX idx_active (active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Project 表创建成功")
        
        # 创建 Account 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL UNIQUE,
                active BOOLEAN DEFAULT TRUE,
                INDEX idx_name (name),
                INDEX idx_active (active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Account 表创建成功")
        
        # 创建 UsageEvent 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usageevent (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tool_id INT NOT NULL,
                user_id INT NOT NULL,
                operator_id INT NOT NULL,
                project_id INT NULL,
                start DATETIME NOT NULL,
                end DATETIME NULL,
                duration INT NULL,
                INDEX idx_tool (tool_id),
                INDEX idx_user (user_id),
                INDEX idx_start (start),
                INDEX idx_end (end)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ UsageEvent 表创建成功")
        
        # 创建 Reservation 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservation (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tool_id INT NOT NULL,
                user_id INT NOT NULL,
                creator_id INT NOT NULL,
                project_id INT NULL,
                start DATETIME NOT NULL,
                end DATETIME NOT NULL,
                short_notice BOOLEAN DEFAULT FALSE,
                cancelled BOOLEAN DEFAULT FALSE,
                missed BOOLEAN DEFAULT FALSE,
                shortened BOOLEAN DEFAULT FALSE,
                INDEX idx_tool (tool_id),
                INDEX idx_user (user_id),
                INDEX idx_start (start),
                INDEX idx_end (end)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Reservation 表创建成功")
        
        # 创建 Area 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS area (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL UNIQUE,
                category VARCHAR(200),
                requires_reservation BOOLEAN DEFAULT FALSE,
                INDEX idx_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Area 表创建成功")
        
        # 创建 AreaAccessRecord 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS areaaccessrecord (
                id INT AUTO_INCREMENT PRIMARY KEY,
                area_id INT NOT NULL,
                customer_id INT NOT NULL,
                project_id INT NULL,
                start DATETIME NOT NULL,
                end DATETIME NULL,
                INDEX idx_area (area_id),
                INDEX idx_customer (customer_id),
                INDEX idx_start (start)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ AreaAccessRecord 表创建成功")
        
        # 创建 StaffCharge 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staffcharge (
                id INT AUTO_INCREMENT PRIMARY KEY,
                staff_member_id INT NOT NULL,
                customer_id INT NOT NULL,
                project_id INT NOT NULL,
                start DATETIME NOT NULL,
                end DATETIME NULL,
                note TEXT,
                INDEX idx_staff (staff_member_id),
                INDEX idx_customer (customer_id),
                INDEX idx_start (start)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ StaffCharge 表创建成功")
        
        # 创建 Consumable 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumable (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category_id INT NULL,
                quantity INT DEFAULT 0,
                visible BOOLEAN DEFAULT TRUE,
                reminder_threshold INT NULL,
                reminder_email TEXT,
                INDEX idx_name (name),
                INDEX idx_visible (visible)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Consumable 表创建成功")
        
        # 创建 ConsumableWithdraw 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumablewithdraw (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                merchant_id INT NOT NULL,
                project_id INT NULL,
                consumable_id INT NOT NULL,
                quantity INT NOT NULL,
                date DATETIME NOT NULL,
                INDEX idx_customer (customer_id),
                INDEX idx_consumable (consumable_id),
                INDEX idx_date (date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ ConsumableWithdraw 表创建成功")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✓ 所有表创建成功！")
        return True
        
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_setup():
    """验证数据库设置"""
    try:
        config = MYSQL_CONFIG.copy()
        config['database'] = DATABASE_NAME
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n数据库中的表 ({len(tables)} 个):")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("NEMO MySQL 数据库初始化")
    print("=" * 60)
    print(f"主机: {MYSQL_CONFIG['host']}")
    print(f"用户: {MYSQL_CONFIG['user']}")
    print(f"数据库: {DATABASE_NAME}")
    print("=" * 60)
    print()
    
    # 步骤 1: 创建数据库
    if not create_database():
        sys.exit(1)
    
    print()
    
    # 步骤 2: 创建表
    if not create_tables():
        sys.exit(1)
    
    print()
    
    # 步骤 3: 验证
    if not verify_setup():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ MySQL 数据库初始化完成！")
    print("=" * 60)
