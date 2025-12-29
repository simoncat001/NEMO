"""
批量重命名PostgreSQL表，去除NEMO_前缀
"""

import psycopg2

def rename_tables():
    print("=" * 60)
    print("批量重命名表：去除 NEMO_ 前缀")
    print("=" * 60)
    print()
    
    try:
        # 询问postgres密码
        import getpass
        print("需要postgres超级用户权限来重命名表")
        print("请输入 PostgreSQL postgres 用户的密码:")
        postgres_password = getpass.getpass("postgres 密码: ")
        print()
        
        # 连接到数据库（使用postgres超级用户）
        conn = psycopg2.connect(
            dbname="nemo_db",
            user="postgres",
            password=postgres_password,
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 查询所有NEMO_开头的表
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'NEMO_%'
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            print("✓ 没有找到需要重命名的表（NEMO_前缀）")
            return
        
        print(f"找到 {len(tables)} 个需要重命名的表\n")
        
        # 批量重命名
        success_count = 0
        error_count = 0
        
        for table in tables:
            old_name = table[0]
            new_name = old_name.replace('NEMO_', '', 1)  # 只替换第一个NEMO_
            
            try:
                sql = f'ALTER TABLE "{old_name}" RENAME TO "{new_name}";'
                cursor.execute(sql)
                print(f"✓ {old_name} → {new_name}")
                success_count += 1
            except Exception as e:
                print(f"✗ {old_name} 重命名失败: {e}")
                error_count += 1
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print(f"✓ 成功: {success_count} 个表")
        if error_count > 0:
            print(f"✗ 失败: {error_count} 个表")
        print("=" * 60)
        print()
        print("提示：迁移文件需要手动删除或修改")
        print("      删除: NEMO/migrations/0138_remove_all_nemo_prefix.py")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    confirm = input("确认要批量重命名所有NEMO_开头的表吗? (yes/no): ").strip().lower()
    if confirm == 'yes':
        rename_tables()
    else:
        print("已取消操作")
