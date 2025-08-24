#!/bin/bash

# Kitako Development Utilities
# Helper script for common development tasks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_color() {
    printf "${1}${2}${NC}\n"
}

show_help() {
    echo "Kitako Development Utilities"
    echo ""
    echo "Usage: ./dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup          - Initial project setup"
    echo "  test           - Run all tests"
    echo "  migrate        - Run database migrations"
    echo "  superuser      - Create Django superuser"
    echo "  reset-db       - Reset database (WARNING: destroys all data)"
    echo "  clean          - Clean cache files and dependencies"
    echo "  lint           - Run linting on frontend code"
    echo "  build          - Build frontend for production"
    echo "  logs           - View application logs"
    echo "  status         - Check application status"
    echo "  help           - Show this help message"
    echo ""
}

setup_project() {
    print_color $BLUE "🔧 Setting up Kitako project..."
    
    # Backend setup
    cd backend
    
    if [ ! -d "venv" ]; then
        print_color $YELLOW "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_color $YELLOW "⚠️  Created .env file. Please update with your settings."
    fi
    
    python manage.py migrate
    
    cd ..
    
    # Frontend setup
    cd frontend
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_color $YELLOW "⚠️  Created frontend .env file."
    fi
    
    npm install
    
    cd ..
    
    print_color $GREEN "✅ Project setup complete!"
}

run_tests() {
    print_color $BLUE "🧪 Running tests..."
    
    cd backend
    source venv/bin/activate
    python run_tests.py
    cd ..
    
    print_color $GREEN "✅ Tests completed!"
}

run_migrations() {
    print_color $BLUE "🔄 Running database migrations..."
    
    cd backend
    source venv/bin/activate
    python manage.py makemigrations
    python manage.py migrate
    cd ..
    
    print_color $GREEN "✅ Migrations completed!"
}

create_superuser() {
    print_color $BLUE "👤 Creating Django superuser..."
    
    cd backend
    source venv/bin/activate
    python manage.py createsuperuser
    cd ..
    
    print_color $GREEN "✅ Superuser created!"
}

reset_database() {
    print_color $RED "⚠️  WARNING: This will destroy all data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_color $YELLOW "Resetting database..."
        
        cd backend
        
        if [ -f "db.sqlite3" ]; then
            rm db.sqlite3
        fi
        
        find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
        find . -path "*/migrations/*.pyc" -delete
        
        source venv/bin/activate
        python manage.py makemigrations
        python manage.py migrate
        
        cd ..
        
        print_color $GREEN "✅ Database reset complete!"
    else
        print_color $YELLOW "Database reset cancelled."
    fi
}

clean_project() {
    print_color $BLUE "🧹 Cleaning project..."
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean frontend node_modules if requested
    read -p "Remove node_modules? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd frontend
        rm -rf node_modules
        rm -f .dependencies_installed
        cd ..
        print_color $YELLOW "Node modules removed. Run 'npm install' before starting frontend."
    fi
    
    print_color $GREEN "✅ Project cleaned!"
}

run_lint() {
    print_color $BLUE "🔍 Running linter..."
    
    cd frontend
    npm run lint
    cd ..
    
    print_color $GREEN "✅ Linting completed!"
}

build_frontend() {
    print_color $BLUE "🏗️  Building frontend for production..."
    
    cd frontend
    npm run build
    cd ..
    
    print_color $GREEN "✅ Frontend build completed!"
}

view_logs() {
    print_color $BLUE "📋 Viewing application logs..."
    
    if [ -f "backend/logs/kitako.log" ]; then
        tail -f backend/logs/kitako.log
    else
        print_color $YELLOW "No log file found. Start the application to generate logs."
    fi
}

check_status() {
    print_color $BLUE "📊 Checking application status..."
    
    # Check if ports are in use
    if nc -z localhost 8000 2>/dev/null; then
        print_color $GREEN "✅ Backend running on port 8000"
    else
        print_color $YELLOW "⚠️  Backend not running on port 8000"
    fi
    
    if nc -z localhost 5173 2>/dev/null; then
        print_color $GREEN "✅ Frontend running on port 5173"
    else
        print_color $YELLOW "⚠️  Frontend not running on port 5173"
    fi
    
    # Check virtual environment
    if [ -d "backend/venv" ]; then
        print_color $GREEN "✅ Python virtual environment exists"
    else
        print_color $YELLOW "⚠️  Python virtual environment not found"
    fi
    
    # Check node_modules
    if [ -d "frontend/node_modules" ]; then
        print_color $GREEN "✅ Node.js dependencies installed"
    else
        print_color $YELLOW "⚠️  Node.js dependencies not installed"
    fi
}

# Main command handling
case "${1:-help}" in
    setup)
        setup_project
        ;;
    test)
        run_tests
        ;;
    migrate)
        run_migrations
        ;;
    superuser)
        create_superuser
        ;;
    reset-db)
        reset_database
        ;;
    clean)
        clean_project
        ;;
    lint)
        run_lint
        ;;
    build)
        build_frontend
        ;;
    logs)
        view_logs
        ;;
    status)
        check_status
        ;;
    help)
        show_help
        ;;
    *)
        print_color $RED "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
