# PostgreSQL 数据库创建指南

## 错误原因
数据库 "nemo_db" 不存在，需要先创建数据库。

## 解决方案

### 方法 1: 使用 pgAdmin（图形界面）

1. 打开 pgAdmin
2. 连接到你的 PostgreSQL 服务器
3. 右键点击 "Databases" -> "Create" -> "Database"
4. 输入数据库名: `nemo_db`
5. 点击 "Save"

然后执行SQL:
```sql
CREATE USER nemo_user WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;
\c nemo_db
GRANT ALL ON SCHEMA public TO nemo_user;
```

### 方法 2: 使用命令行 (psql)

打开 "SQL Shell (psql)" 或 PowerShell，然后执行:

```powershell
# 以 postgres 用户连接
psql -U postgres

# 在 psql 中执行以下命令:
```

```sql
CREATE DATABASE nemo_db WITH ENCODING 'UTF8';
CREATE USER nemo_user WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;
\c nemo_db
GRANT ALL ON SCHEMA public TO nemo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO nemo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO nemo_user;
\q
```

### 方法 3: 使用 PowerShell 一键执行

```powershell
# 确保 psql 在环境变量中
psql -U postgres -c "CREATE DATABASE nemo_db WITH ENCODING 'UTF8';"
psql -U postgres -c "CREATE USER nemo_user WITH PASSWORD '123456';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;"
psql -U postgres -d nemo_db -c "GRANT ALL ON SCHEMA public TO nemo_user;"
psql -U postgres -d nemo_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO nemo_user;"
```

## 创建数据库后，运行迁移

```powershell
cd D:\Data\Code\NEMO
$env:DJANGO_SETTINGS_MODULE="resources.settings"
python manage.py migrate
```

## 当前数据库配置

- 数据库名: `nemo_db`
- 用户名: `nemo_user`
- 密码: `123456`
- 主机: `localhost`
- 端口: `5432`

## 检查 PostgreSQL 服务是否运行

```powershell
# 检查服务状态
Get-Service -Name *postgre*

# 启动服务（如果未运行）
Start-Service postgresql-x64-*
```

## 需要修改配置？

如果你想使用不同的数据库名或密码，请修改 `resources/settings.py` 中的 DATABASES 配置。
