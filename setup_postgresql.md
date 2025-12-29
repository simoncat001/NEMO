# PostgreSQL 数据库设置指南

## 步骤 1: 安装 PostgreSQL 驱动

```powershell
pip install psycopg2-binary
```

## 步骤 2: 安装并配置 PostgreSQL

### 方式 A: 使用 Docker (推荐)

```powershell
# 启动 PostgreSQL 容器
docker run --name nemo-postgres `
  -e POSTGRES_DB=nemo_db `
  -e POSTGRES_USER=nemo_user `
  -e POSTGRES_PASSWORD=nemo_password `
  -p 5432:5432 `
  -d postgres:16
```

### 方式 B: 本地安装 PostgreSQL

1. 下载并安装 PostgreSQL: https://www.postgresql.org/download/windows/
2. 安装后，使用 pgAdmin 或命令行创建数据库：

```sql
CREATE DATABASE nemo_db;
CREATE USER nemo_user WITH PASSWORD 'nemo_password';
ALTER ROLE nemo_user SET client_encoding TO 'utf8';
ALTER ROLE nemo_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE nemo_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;
```

## 步骤 3: 运行数据库迁移创建表

```powershell
# 进入项目目录
cd d:\Data\Code\NEMO

# 运行迁移命令创建所有表
python manage.py migrate
```

## 步骤 4: 创建超级管理员账户

```powershell
python manage.py createsuperuser
```

## 步骤 5: 启动开发服务器

```powershell
python manage.py runserver
```

然后访问: http://localhost:8000

## 数据库配置说明

当前配置位置: `resources/settings.py`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "nemo_db",           # 数据库名
        "USER": "nemo_user",          # 用户名
        "PASSWORD": "nemo_password",  # 密码（请修改为更安全的密码）
        "HOST": "localhost",          # 数据库主机
        "PORT": "5432",              # 端口
    }
}
```

## 安全提示

⚠️ **重要**: 在生产环境中，请务必：
1. 修改默认密码为强密码
2. 将数据库配置移至环境变量
3. 不要将密码提交到版本控制系统

## 可选: 使用环境变量

创建 `.env` 文件：

```env
DB_NAME=nemo_db
DB_USER=nemo_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432
```

然后修改 `settings.py` 使用环境变量：

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "nemo_db"),
        "USER": os.getenv("DB_USER", "nemo_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "nemo_password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
```
