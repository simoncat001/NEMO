import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='12345678',
    database='nemo',
    charset='utf8mb4'
)

cursor = connection.cursor()

# 创建 consumable_withdraw 表
try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumable_withdraw (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            consumable_id INT NOT NULL,
            project_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
            amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT '总金额',
            date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_cw_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            CONSTRAINT fk_cw_consumable FOREIGN KEY (consumable_id) REFERENCES consumable(id) ON DELETE CASCADE,
            CONSTRAINT fk_cw_project FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    print('✓ 创建 consumable_withdraw 表成功')
except Exception as e:
    print(f'✗ 创建 consumable_withdraw 表失败: {e}')

connection.commit()
cursor.close()
connection.close()
