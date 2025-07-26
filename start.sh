#!/bin/bash

echo "=== 狼人杀推理助手启动脚本 ==="

# 检查Python是否安装
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python"
    exit 1
fi

# 检查Django是否安装
if ! python -c "import django" &> /dev/null; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

# 检查数据库是否需要迁移
if [ ! -f "db.sqlite3" ]; then
    echo "初始化数据库..."
    python manage.py makemigrations
    python manage.py migrate
fi

echo "启动开发服务器..."
echo "访问地址: http://127.0.0.1:8000"
echo "按 Ctrl+C 停止服务器"
echo ""

python manage.py runserver 