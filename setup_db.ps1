# NEMO PostgreSQL 数据库设置脚本 (Python 3.12)
# 使用方法: .\setup_db.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "NEMO PostgreSQL 数据库设置" -ForegroundColor Cyan
Write-Host "Python 3.12 版本" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 版本
Write-Host "1. 检查 Python 版本..." -ForegroundColor Yellow
python --version

# 检查 psycopg2 是否已安装
Write-Host ""
Write-Host "2. 检查 PostgreSQL 驱动..." -ForegroundColor Yellow
python -c "import psycopg2; print('psycopg2 版本:', psycopg2.__version__)"

if ($LASTEXITCODE -ne 0) {
    Write-Host "正在安装 psycopg2-binary..." -ForegroundColor Yellow
    pip install psycopg2-binary
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "数据库配置信息:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "数据库名: nemo_db"
Write-Host "用户名: nemo_user"
Write-Host "密码: nemo_password"
Write-Host "主机: localhost"
Write-Host "端口: 5432"
Write-Host ""

# 选择数据库设置方式
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "请选择 PostgreSQL 设置方式:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "1. 使用 Docker (推荐，快速启动)"
Write-Host "2. 使用已安装的本地 PostgreSQL"
Write-Host "3. 跳过数据库设置，直接运行迁移"
Write-Host ""

$choice = Read-Host "请输入选项 (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "正在使用 Docker 启动 PostgreSQL..." -ForegroundColor Yellow
        
        # 检查容器是否已存在
        $existing = docker ps -a --filter "name=nemo-postgres" --format "{{.Names}}"
        
        if ($existing -eq "nemo-postgres") {
            Write-Host "容器已存在，正在启动..." -ForegroundColor Yellow
            docker start nemo-postgres
        } else {
            Write-Host "创建新的 PostgreSQL 容器..." -ForegroundColor Yellow
            docker run --name nemo-postgres `
                -e POSTGRES_DB=nemo_db `
                -e POSTGRES_USER=nemo_user `
                -e POSTGRES_PASSWORD=nemo_password `
                -p 5432:5432 `
                -d postgres:16
        }
        
        Write-Host "等待 PostgreSQL 启动..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
    "2" {
        Write-Host ""
        Write-Host "请确保 PostgreSQL 服务已启动，并执行以下 SQL:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "CREATE DATABASE nemo_db;" -ForegroundColor Green
        Write-Host "CREATE USER nemo_user WITH PASSWORD 'nemo_password';" -ForegroundColor Green
        Write-Host "GRANT ALL PRIVILEGES ON DATABASE nemo_db TO nemo_user;" -ForegroundColor Green
        Write-Host ""
        $continue = Read-Host "已完成数据库创建？(Y/N)"
        if ($continue -ne "Y" -and $continue -ne "y") {
            Write-Host "已取消" -ForegroundColor Red
            exit
        }
    }
    "3" {
        Write-Host ""
        Write-Host "跳过数据库设置..." -ForegroundColor Yellow
    }
    default {
        Write-Host "无效选项" -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "3. 运行数据库迁移创建表..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 设置环境变量
$env:DJANGO_SETTINGS_MODULE = "resources.settings"
$env:PYTHONPATH = "D:\Data\Code\NEMO"

# 运行迁移
Write-Host ""
Write-Host "执行: python manage.py migrate" -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "✓ 数据库表创建成功！" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步操作:" -ForegroundColor Cyan
    Write-Host "1. 创建超级管理员: python manage.py createsuperuser"
    Write-Host "2. 启动服务器: python manage.py runserver"
    Write-Host "3. 访问: http://localhost:8000"
} else {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "✗ 迁移失败，请检查数据库连接" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
}
