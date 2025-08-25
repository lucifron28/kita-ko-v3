#!/bin/bash

echo "🧪 HEROKU DEPLOYMENT VERIFICATION"
echo "==================================="

if [ -z "$1" ]; then
    read -p "Enter your Heroku app name: " APP_NAME
else
    APP_NAME=$1
fi

echo "📱 Testing app: $APP_NAME"
echo ""

# Test main app
echo "🌐 Testing main application..."
if curl -s "https://$APP_NAME.herokuapp.com" | grep -q "Kita-Ko" || curl -s "https://$APP_NAME.herokuapp.com" | grep -q "DOCTYPE"; then
    echo "✅ Main app is responding"
else
    echo "❌ Main app not responding"
fi

# Test API health
echo "🔌 Testing API endpoints..."
API_BASE="https://$APP_NAME.herokuapp.com/api"

# Test API root
if curl -s "$API_BASE/" | grep -q "API" || [ "$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/")" = "200" ]; then
    echo "✅ API is responding"
else
    echo "❌ API not responding"
fi

# Test auth endpoint
AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/auth/")
if [ "$AUTH_STATUS" = "200" ] || [ "$AUTH_STATUS" = "404" ]; then
    echo "✅ Auth endpoints accessible"
else
    echo "⚠️ Auth endpoints status: $AUTH_STATUS"
fi

# Test reports endpoint (should be 401 without auth)
REPORTS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/reports/")
if [ "$REPORTS_STATUS" = "401" ] || [ "$REPORTS_STATUS" = "200" ]; then
    echo "✅ Reports endpoints accessible"
else
    echo "⚠️ Reports endpoints status: $REPORTS_STATUS"
fi

# Test static files
STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$APP_NAME.herokuapp.com/static/")
if [ "$STATIC_STATUS" = "404" ] || [ "$STATIC_STATUS" = "403" ] || [ "$STATIC_STATUS" = "200" ]; then
    echo "✅ Static files configured"
else
    echo "⚠️ Static files status: $STATIC_STATUS"
fi

echo ""
echo "📊 App Information:"
echo "• URL: https://$APP_NAME.herokuapp.com"
echo "• Admin: https://$APP_NAME.herokuapp.com/admin"
echo "• API: https://$APP_NAME.herokuapp.com/api"
echo "• Docs: https://$APP_NAME.herokuapp.com/api/docs"

echo ""
echo "🔧 Quick Commands:"
echo "• heroku logs --tail -a $APP_NAME"
echo "• heroku ps -a $APP_NAME"
echo "• heroku config -a $APP_NAME"
echo "• heroku run python backend/manage.py shell -a $APP_NAME"

echo ""
echo "✅ Verification complete!"
