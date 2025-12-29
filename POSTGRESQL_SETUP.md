# NEMO + PostgreSQL 设置指南 (Python 3.12)

## 当前状态
✓ Python 3.12.11 已安装
✓ psycopg2-binary 2.9.9 已安装
✓ settings.py 已配置为使用 PostgreSQL

## 接下来的步骤

### 选项 1: 使用本地 PostgreSQL (如果已安装)

#### 步骤 1: 创建数据库和用户
在 Windows 搜索中找到 "SQL Shell (psql)" 或使用 pgAdmin，然后执行：

```sql
CREATE DATABASE nemo_db WITH ENCODING 'UTF8';
CREATE USER nemo_user WITH PASSWORD 'nemo_password';
GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;
```

或者在 PowerShell 中执行（如果 psql 在 PATH 中）：
```powershell
psql -U postgres -c "CREATE DATABASE nemo_db WITH ENCODING 'UTF8';"
psql -U postgres -c "CREATE USER nemo_user WITH PASSWORD 'nemo_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;"
```

#### 步骤 2: 运行迁移创建表
```powershell
cd D:\Data\Code\NEMO
python manage.py migrate
```

### 选项 2: 如果没有 PostgreSQL，先安装

#### 方式 A: 使用 PostgreSQL 安装包
1. 下载: https://www.postgresql.org/download/windows/
2. 安装后，记住设置的 postgres 用户密码
3. 然后执行上面的步骤 1 和步骤 2

#### 方式 B: 使用 Chocolatey (包管理器)
```powershell
choco install postgresql16
```

### 快速测试命令

测试数据库连接：
```powershell
python -c "import psycopg2; print('PostgreSQL 驱动已安装')"
```

查看 Django 配置：
```powershell
python manage.py check
```

### 完整设置流程（一次性执行）

```powershell
# 1. 确保在正确的目录
cd D:\Data\Code\NEMO

# 2. 检查 Django 配置
python manage.py check

# 3. 运行迁移（创建所有表）
python manage.py migrate

# 4. 创建超级管理员
python manage.py createsuperuser

# 5. 加载初始数据（可选）
# python manage.py loaddata resources/fixtures/*.json

# 6. 启动开发服务器
python manage.py runserver
```

然后访问: http://localhost:8000

## 数据库配置（已设置）

位置: `resources/settings.py`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "nemo_db",
        "USER": "nemo_user",
        "PASSWORD": "nemo_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

## 如果遇到问题

### 连接错误
- 确保 PostgreSQL 服务正在运行
- Windows 服务中查找 "postgresql" 服务
- 或在任务管理器中查看 postgres.exe 进程

### 权限错误
确保用户有足够权限：
```sql
-- 以 postgres 用户登录后执行
\c nemo_db
GRANT ALL ON SCHEMA public TO nemo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO nemo_user;
```

### 编码错误
如果遇到 UTF-8 编码问题，重新创建数据库：
```sql
DROP DATABASE IF EXISTS nemo_db;
CREATE DATABASE nemo_db WITH ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C' TEMPLATE=template0;
```

## 需要帮助？

运行以下命令获取更多信息：
```powershell
python manage.py --help
python manage.py migrate --help
```
