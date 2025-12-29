"""
创建NEMO PostgreSQL数据库的脚本
使用方法: python create_nemo_database.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    print("=" * 60)
    print("NEMO PostgreSQL 数据库创建脚本")
    print("=" * 60)
    print()
    
    # 数据库配置
    db_name = "nemo_db"
    db_user = "nemo_user"
    db_password = "123456"
    
    # 询问postgres密码
    import getpass
    print("请输入 PostgreSQL postgres 用户的密码:")
    print("(如果没有密码，直接按 Enter)")
    postgres_password = getpass.getpass("postgres 密码: ")
    print()
    
    try:
        # 连接到默认的postgres数据库
        print("1. 连接到 PostgreSQL 服务器...")
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=postgres_password,
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("   ✓ 连接成功")
        print()
        
        # 检查数据库是否已存在
        print(f"2. 检查数据库 '{db_name}' 是否存在...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"   ! 数据库 '{db_name}' 已存在")
            drop = input("   是否删除并重新创建? (y/N): ").strip().lower()
            if drop == 'y':
                print(f"   正在删除数据库 '{db_name}'...")
                # 先断开所有连接
                cursor.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{db_name}'
                    AND pid <> pg_backend_pid()
                """)
                cursor.execute(f"DROP DATABASE {db_name}")
                print(f"   ✓ 已删除数据库 '{db_name}'")
            else:
                print("   跳过数据库创建")
                cursor.close()
                conn.close()
                return False
        
        # 创建数据库
        if not exists or drop == 'y':
            print(f"   正在创建数据库 '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name} WITH ENCODING 'UTF8'")
            print(f"   ✓ 数据库 '{db_name}' 创建成功")
        print()
        
        # 检查用户是否已存在
        print(f"3. 检查用户 '{db_user}' 是否存在...")
        cursor.execute(f"SELECT 1 FROM pg_user WHERE usename = '{db_user}'")
        user_exists = cursor.fetchone()
        
        if user_exists:
            print(f"   ! 用户 '{db_user}' 已存在")
        else:
            print(f"   正在创建用户 '{db_user}'...")
            cursor.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            print(f"   ✓ 用户 '{db_user}' 创建成功")
        print()
        
        # 授予权限
        print(f"4. 授予权限...")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        print(f"   ✓ 已授予所有权限")
        
        cursor.close()
        conn.close()
        
        # 连接到新创建的数据库并设置schema权限
        print(f"5. 设置 schema 权限...")
        conn = psycopg2.connect(
            dbname=db_name,
            user="postgres",
            password=postgres_password,
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {db_user}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {db_user}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {db_user}")
        print(f"   ✓ Schema 权限设置完成")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✓ 数据库创建成功！")
        print("=" * 60)
        print()
        print("数据库配置:")
        print(f"  数据库名: {db_name}")
        print(f"  用户名: {db_user}")
        print(f"  密码: {db_password}")
        print(f"  主机: localhost")
        print(f"  端口: 5432")
        print()
        print("下一步: 运行迁移创建表")
        print("  python manage.py migrate")
        print()
        
        return True
        
    except psycopg2.OperationalError as e:
        print()
        print("=" * 60)
        print("✗ 连接失败")
        print("=" * 60)
        print()
        print(f"错误信息: {e}")
        print()
        print("可能的原因:")
        print("  1. PostgreSQL 服务未运行")
        print("  2. postgres 用户密码不正确")
        print("  3. PostgreSQL 连接配置错误")
        print()
        print("解决方案:")
        print("  1. 检查 PostgreSQL 服务是否运行")
        print("     Get-Service | Where-Object {$_.Name -like '*postgres*'}")
        print()
        print("  2. 如果 postgres 用户有密码，请修改此脚本第22行")
        print("     password='你的postgres密码'")
        print()
        print("  3. 或者使用 pgAdmin 手动创建数据库")
        print("     参考: CREATE_DATABASE.md")
        print()
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ 发生错误")
        print("=" * 60)
        print(f"错误信息: {e}")
        print()
        return False

if __name__ == "__main__":
    success = create_database()
    if not success:
        exit(1)
