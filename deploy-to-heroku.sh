#!/bin/bash

echo "🚀 DEPLOYING KITA-KO V3 TO HEROKU"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Get app name from user
read -p "Enter your Heroku app name: " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App name is required"
    exit 1
fi

echo "📱 App name: $APP_NAME"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI found"

# Login to Heroku
echo "🔐 Logging into Heroku..."
heroku auth:whoami > /dev/null 2>&1 || heroku login

# Check if app exists, if not create it
echo "🏗️ Setting up Heroku app..."
if heroku apps:info $APP_NAME > /dev/null 2>&1; then
    echo "✅ App '$APP_NAME' already exists"
else
    echo "📱 Creating new Heroku app '$APP_NAME'..."
    heroku create $APP_NAME
fi

# Add buildpacks
echo "🔧 Configuring buildpacks..."
heroku buildpacks:clear -a $APP_NAME
heroku buildpacks:add --index 1 heroku/nodejs -a $APP_NAME
heroku buildpacks:add --index 2 heroku/python -a $APP_NAME

# Add PostgreSQL database
echo "🗄️ Setting up database..."
heroku addons:create heroku-postgresql:essential-0 -a $APP_NAME 2>/dev/null || echo "✅ Database already exists"

# Generate and set environment variables
echo "🔐 Setting up environment variables..."

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
heroku config:set SECRET_KEY="$SECRET_KEY" -a $APP_NAME

# Set basic config
heroku config:set DEBUG=False -a $APP_NAME
heroku config:set ALLOWED_HOSTS="$APP_NAME.herokuapp.com" -a $APP_NAME

# Generate encryption key (32 characters)
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24)[:32])")
heroku config:set FIELD_ENCRYPTION_KEY="$ENCRYPTION_KEY" -a $APP_NAME

# Set API configuration
heroku config:set OPENROUTER_BASE_URL="https://openrouter.ai/api/v1" -a $APP_NAME

# Set frontend URL for QR codes and verification
heroku config:set FRONTEND_URL="https://$APP_NAME.herokuapp.com" -a $APP_NAME

# Prompt for API key
echo ""
echo "🤖 API KEY SETUP"
echo "=================="
echo "You need an OpenRouter API key for AI features."
echo "Get one at: https://openrouter.ai/keys"
echo ""
read -p "Enter your OpenRouter API key (or press Enter to set it later): " API_KEY

if [ ! -z "$API_KEY" ]; then
    heroku config:set OPENROUTER_API_KEY="$API_KEY" -a $APP_NAME
    echo "✅ API key configured"
else
    echo "⚠️ API key not set. You can set it later with:"
    echo "   heroku config:set OPENROUTER_API_KEY='your-key-here' -a $APP_NAME"
fi

# Update CORS settings for production
echo "🌐 Updating CORS settings..."
heroku config:set CORS_ALLOWED_ORIGINS="https://$APP_NAME.herokuapp.com" -a $APP_NAME

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."
if [ -f "pre-deploy-check.sh" ]; then
    bash pre-deploy-check.sh
else
    echo "⚠️ Pre-deploy check script not found, skipping..."
fi

# Commit latest changes
echo "📝 Committing latest changes..."
git add .
git commit -m "Deploy to Heroku: Add draft status migration and deployment fixes" || echo "No changes to commit"

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
echo "This may take a few minutes..."

if git push heroku main; then
    echo "✅ Deployment successful!"
else
    echo "❌ Deployment failed. Check the logs:"
    echo "   heroku logs --tail -a $APP_NAME"
    exit 1
fi

# Run database migrations (including the new draft status migration)
echo "🗄️ Running database migrations..."
heroku run python backend/manage.py migrate -a $APP_NAME

# Create superuser (optional)
echo ""
read -p "Do you want to create a superuser account? (y/n): " CREATE_SUPERUSER

if [ "$CREATE_SUPERUSER" = "y" ] || [ "$CREATE_SUPERUSER" = "Y" ]; then
    echo "👤 Creating superuser..."
    heroku run python backend/manage.py createsuperuser -a $APP_NAME
fi

# Show deployment info
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo "🌐 App URL: https://$APP_NAME.herokuapp.com"
echo "🔧 Admin: https://$APP_NAME.herokuapp.com/admin"
echo "📖 API Docs: https://$APP_NAME.herokuapp.com/api/docs"
echo ""

# Test the deployment
echo "🧪 Testing deployment..."
if curl -s "https://$APP_NAME.herokuapp.com" > /dev/null; then
    echo "✅ App is responding"
else
    echo "⚠️ App might not be ready yet. Check logs:"
    echo "   heroku logs --tail -a $APP_NAME"
fi

echo ""
echo "📋 IMPORTANT NOTES:"
echo "==================="
echo "• The app includes the draft status fix for PDF generation"
echo "• All existing reports have been migrated to use the new status system"
echo "• Users will now see 'Generate PDF' buttons for draft reports"
echo "• PDF generation workflow: Draft → Generating → Completed"
echo ""

if [ -z "$API_KEY" ]; then
    echo "⚠️ REMEMBER TO SET YOUR API KEY:"
    echo "   heroku config:set OPENROUTER_API_KEY='your-key-here' -a $APP_NAME"
    echo ""
fi

echo "📊 Useful commands:"
echo "• View logs: heroku logs --tail -a $APP_NAME"
echo "• Open app: heroku open -a $APP_NAME"
echo "• Run Django shell: heroku run python backend/manage.py shell -a $APP_NAME"
echo "• Scale dynos: heroku ps:scale web=1 -a $APP_NAME"
echo ""
echo "🎯 Next steps:"
echo "1. Test all functionality on the deployed app"
echo "2. Create test reports and verify PDF generation works"
echo "3. Set up monitoring and error tracking"
echo ""
echo "Happy deploying! 🚀"
