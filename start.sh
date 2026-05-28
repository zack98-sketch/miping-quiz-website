#!/bin/bash
# 启动密评题库答题网站

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== 密评题库答题网站启动脚本 ==="

# Start backend
echo "Starting backend server..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID (port 8000)"

# Start frontend dev server
echo "Starting frontend dev server..."
cd "$SCRIPT_DIR/frontend"
npx vite --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID (port 5173)"

echo ""
echo "=== 服务已启动 ==="
echo "后端 API: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "前端页面: http://localhost:5173"
echo ""
echo "默认管理员: admin / admin123"
echo ""
echo "按 Ctrl+C 停止所有服务"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Services stopped'; exit 0" INT TERM
wait
