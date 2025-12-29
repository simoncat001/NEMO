-- NEMO PostgreSQL 数据库初始化脚本
-- 使用方法: 在 psql 或 pgAdmin 中执行此脚本

-- 创建数据库
CREATE DATABASE nemo_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- 创建用户
CREATE USER nemo_user WITH PASSWORD 'nemo_password';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;

-- 连接到 nemo_db 数据库后执行（如果 PostgreSQL 版本 >= 15）
\c nemo_db
GRANT ALL ON SCHEMA public TO nemo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO nemo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO nemo_user;
