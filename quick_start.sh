#!/bin/bash

echo "Starting Kitako Application..."

if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Please run this script from the project root directory"
    exit 1
fi

cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting Django backend..."
cd backend
source venv/bin/activate 2>/dev/null || {
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

python manage.py migrate --noinput >/dev/null 2>&1

python manage.py runserver 8000 &
BACKEND_PID=$!

cd ..

echo "Starting React frontend..."
cd frontend

[ ! -d "node_modules" ] && npm install

npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ Application started!"
echo "🔗 Frontend: http://localhost:5173"
echo "🔗 Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

wait
