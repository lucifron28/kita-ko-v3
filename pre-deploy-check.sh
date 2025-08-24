#!/bin/bash

echo "🚀 Pre-deployment checklist for Kita-Ko v3"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "✅ Running from project root"

# Check required files
echo "🔍 Checking required deployment files..."

required_files=(
    "Procfile"
    "runtime.txt" 
    "package.json"
    "bin/post_compile"
    ".env.example"
    "backend/requirements.txt"
    "frontend/package.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

# Test frontend build
echo "🏗️ Testing frontend build..."
cd frontend
if npm run build; then
    echo "✅ Frontend build successful"
    cd ..
else
    echo "❌ Frontend build failed"
    cd ..
    exit 1
fi

# Check backend dependencies
echo "🐍 Checking backend dependencies..."
cd backend
if pip install -r requirements.txt --dry-run > /dev/null 2>&1; then
    echo "✅ Backend dependencies look good"
else
    echo "⚠️ Some backend dependencies might have issues"
fi

# Check Django configuration
if python manage.py check --deploy > /dev/null 2>&1; then
    echo "✅ Django deployment check passed"
else
    echo "⚠️ Django deployment check has warnings"
    python manage.py check --deploy
fi

cd ..

# Check environment variables
echo "📋 Environment variables checklist:"
echo "   □ SECRET_KEY - Generate a new secret key for production"
echo "   □ DEBUG - Set to False"
echo "   □ ALLOWED_HOSTS - Set to your domain"
echo "   □ OPENROUTER_API_KEY - Required for AI features"
echo "   □ FIELD_ENCRYPTION_KEY - 32-character encryption key"
echo ""
echo "   See .env.example for all required variables"

echo ""
echo "🎉 Pre-deployment check complete!"
echo ""
echo "Next steps:"
echo "1. Create Heroku app: heroku create your-app-name"
echo "2. Add buildpacks:"
echo "   heroku buildpacks:add --index 1 heroku/nodejs"
echo "   heroku buildpacks:add --index 2 heroku/python"
echo "3. Add database: heroku addons:create heroku-postgresql:mini"
echo "4. Set environment variables (see DEPLOYMENT.md)"
echo "5. Deploy: git push heroku main"
