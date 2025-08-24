#!/bin/bash

# Kitako Full Stack Application Runner
# This script sets up and runs both backend (Django) and frontend (React) servers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

# Function to print section headers
print_header() {
    echo
    print_color $CYAN "=========================================="
    print_color $CYAN "$1"
    print_color $CYAN "=========================================="
    echo
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is available
port_available() {
    ! nc -z localhost $1 >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_color $YELLOW "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" >/dev/null 2>&1; then
            print_color $GREEN "$service_name is ready!"
            return 0
        fi
        
        printf "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_color $RED "$service_name failed to start within expected time"
    return 1
}

# Function to cleanup background processes
cleanup() {
    print_color $YELLOW "\n🛑 Shutting down services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        print_color $YELLOW "Stopping Django server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        print_color $YELLOW "Stopping React server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_color $GREEN "✅ Services stopped successfully"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Main script starts here
print_header "🚀 KITAKO FULL STACK APPLICATION RUNNER"

# Check system requirements
print_header "🔍 CHECKING SYSTEM REQUIREMENTS"

if ! command_exists python3; then
    print_color $RED "❌ Python3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    print_color $RED "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    print_color $RED "❌ npm is required but not installed"
    exit 1
fi

print_color $GREEN "✅ Python3 version: $(python3 --version)"
print_color $GREEN "✅ Node.js version: $(node --version)"
print_color $GREEN "✅ npm version: $(npm --version)"

# Check if required ports are available
BACKEND_PORT=8000
FRONTEND_PORT=5173

if ! port_available $BACKEND_PORT; then
    print_color $RED "❌ Port $BACKEND_PORT is already in use (needed for Django)"
    print_color $YELLOW "Please stop the service using port $BACKEND_PORT and try again"
    exit 1
fi

if ! port_available $FRONTEND_PORT; then
    print_color $RED "❌ Port $FRONTEND_PORT is already in use (needed for React)"
    print_color $YELLOW "Please stop the service using port $FRONTEND_PORT and try again"
    exit 1
fi

print_color $GREEN "✅ Required ports are available"

# Setup backend
print_header "🐍 SETTING UP DJANGO BACKEND"

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_color $YELLOW "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_color $YELLOW "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/.requirements_installed" ]; then
    print_color $YELLOW "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.requirements_installed
    print_color $GREEN "✅ Python dependencies installed"
else
    print_color $GREEN "✅ Python dependencies already installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_color $YELLOW "Creating .env file from template..."
    cp .env.example .env
    print_color $YELLOW "⚠️  Please update .env file with your configuration"
fi

# Run database migrations
print_color $YELLOW "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create superuser if needed (optional)
print_color $YELLOW "Checking for superuser..."
if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('EXISTS' if User.objects.filter(is_superuser=True).exists() else 'NONE')" | grep -q "NONE"; then
    print_color $YELLOW "No superuser found. You can create one later with: python manage.py createsuperuser"
fi

# Collect static files (if needed for production)
if [ "$NODE_ENV" = "production" ]; then
    print_color $YELLOW "Collecting static files..."
    python manage.py collectstatic --noinput
fi

print_color $GREEN "✅ Backend setup complete"

# Start Django server in background
print_color $YELLOW "Starting Django server on http://localhost:$BACKEND_PORT..."
python manage.py runserver 0.0.0.0:$BACKEND_PORT &
BACKEND_PID=$!

cd ..

# Setup frontend
print_header "⚛️  SETTING UP REACT FRONTEND"

cd frontend

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_color $YELLOW "Creating frontend .env file from template..."
    cp .env.example .env
fi

# Install npm dependencies
if [ ! -d "node_modules" ] || [ ! -f ".dependencies_installed" ]; then
    print_color $YELLOW "Installing Node.js dependencies..."
    npm install
    touch .dependencies_installed
    print_color $GREEN "✅ Node.js dependencies installed"
else
    print_color $GREEN "✅ Node.js dependencies already installed"
fi

# Build frontend (if production)
if [ "$NODE_ENV" = "production" ]; then
    print_color $YELLOW "Building frontend for production..."
    npm run build
fi

print_color $GREEN "✅ Frontend setup complete"

# Start React development server in background
print_color $YELLOW "Starting React server on http://localhost:$FRONTEND_PORT..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Wait for services to be ready
print_header "🔄 WAITING FOR SERVICES TO START"

# Wait for backend
wait_for_service "http://localhost:$BACKEND_PORT" "Django Backend"

# Wait for frontend
wait_for_service "http://localhost:$FRONTEND_PORT" "React Frontend"

# Display success message and instructions
print_header "🎉 APPLICATION READY"

print_color $GREEN "✅ Kitako application is now running!"
echo
print_color $CYAN "🔗 Application URLs:"
print_color $BLUE "   • Frontend (React):     http://localhost:$FRONTEND_PORT"
print_color $BLUE "   • Backend API (Django): http://localhost:$BACKEND_PORT"
print_color $BLUE "   • Admin Interface:      http://localhost:$BACKEND_PORT/admin"
print_color $BLUE "   • API Documentation:    http://localhost:$BACKEND_PORT/api/docs"
echo
print_color $PURPLE "📊 Service Status:"
print_color $GREEN "   • Django Server PID:    $BACKEND_PID"
print_color $GREEN "   • React Server PID:     $FRONTEND_PID"
echo
print_color $YELLOW "⚡ Quick Commands:"
print_color $BLUE "   • Run tests:            cd backend && python manage.py test"
print_color $BLUE "   • Create superuser:     cd backend && python manage.py createsuperuser"
print_color $BLUE "   • View logs:            tail -f backend/logs/kitako.log"
echo
print_color $CYAN "💡 Press Ctrl+C to stop both servers"
echo

# Keep script running and monitor services
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_color $RED "❌ Django server stopped unexpectedly"
        break
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_color $RED "❌ React server stopped unexpectedly"
        break
    fi
    
    sleep 5
done

print_color $RED "❌ One or more services have stopped"
exit 1
