"""
验证PostgreSQL数据库中的表名
检查是否成功去除了NEMO_前缀
"""

import psycopg2

def check_tables():
    print("=" * 60)
    print("检查 NEMO 数据库表名")
    print("=" * 60)
    print()
    
    try:
        # 连接到数据库
        conn = psycopg2.connect(
            dbname="nemo_db",
            user="nemo_user",
            password="123456",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # 查询所有表名
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        
        print(f"数据库中共有 {len(tables)} 个表\n")
        
        # 分类统计
        nemo_prefix_tables = []
        other_tables = []
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('NEMO_'):
                nemo_prefix_tables.append(table_name)
            else:
                other_tables.append(table_name)
        
        # 显示结果
        if nemo_prefix_tables:
            print(f"⚠ 仍有 {len(nemo_prefix_tables)} 个表带有 NEMO_ 前缀:")
            print("-" * 60)
            for table in nemo_prefix_tables[:20]:  # 只显示前20个
                print(f"  - {table}")
            if len(nemo_prefix_tables) > 20:
                print(f"  ... 还有 {len(nemo_prefix_tables) - 20} 个表")
            print()
        else:
            print("✓ 没有表带有 NEMO_ 前缀")
            print()
        
        print(f"✓ 其他表 ({len(other_tables)} 个):")
        print("-" * 60)
        
        # 显示已重命名的关键表
        renamed_tables = [
            'tool_backup_owners',
            'tool_superusers', 
            'tool_staff',
            'tool_adjustment_request_reviewers',
            'user_qualifications'
        ]
        
        found_renamed = []
        for table in renamed_tables:
            if table in [t[0] for t in tables]:
                found_renamed.append(table)
        
        if found_renamed:
            print("已成功重命名的表:")
            for table in found_renamed:
                print(f"  ✓ {table}")
            print()
        
        # 显示其他一些主要表
        print("其他主要表 (前20个):")
        for table in other_tables[:20]:
            print(f"  - {table}")
        if len(other_tables) > 20:
            print(f"  ... 还有 {len(other_tables) - 20} 个表")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        if not nemo_prefix_tables:
            print("✓ 所有表名前缀已成功修改！")
        else:
            print("⚠ 部分表仍需手动处理")
        print("=" * 60)
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_tables()
