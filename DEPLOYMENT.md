# Heroku Deployment Guide for Kita-Ko v3

## 🚀 Full-Stack Deployment on Heroku

This guide will help you deploy your Django + React application on Heroku.

### Prerequisites
1. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
2. Git repository initialized
3. Heroku account created

### Step 1: Create Heroku Application

```bash
# Login to Heroku
heroku login

# Create new Heroku app
heroku create your-app-name

# Add buildpacks (Node.js first, then Python)
heroku buildpacks:add --index 1 heroku/nodejs
heroku buildpacks:add --index 2 heroku/python
```

### Step 2: Add Database

```bash
# Add PostgreSQL database
heroku addons:create heroku-postgresql:mini
```

### Step 3: Configure Environment Variables

```bash
# Set environment variables
heroku config:set SECRET_KEY="your-super-secret-key-here-change-this"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
heroku config:set OPENROUTER_API_KEY="your-openrouter-api-key"
heroku config:set FIELD_ENCRYPTION_KEY="your-32-character-encryption-key"

# Optional: Set additional variables
heroku config:set OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
```

### Step 4: Deploy Application

```bash
# Add files to git
git add .
git commit -m "Prepare for Heroku deployment"

# Deploy to Heroku
git push heroku main
```

### Step 5: Run Initial Setup

```bash
# Run database migrations
heroku run python backend/manage.py migrate

# Create superuser (optional)
heroku run python backend/manage.py createsuperuser

# Check logs
heroku logs --tail
```

### Step 6: Open Your Application

```bash
# Open in browser
heroku open
```

## 🔧 Configuration Details

### Buildpacks Used
1. **heroku/nodejs** - Builds React frontend
2. **heroku/python** - Runs Django backend

### Build Process
1. Node.js buildpack installs frontend dependencies and builds React
2. Python buildpack installs backend dependencies
3. `post_compile` script collects static files
4. Django serves both API and React app

### Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-change-me` |
| `DEBUG` | Debug mode (False for production) | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `your-app.herokuapp.com` |
| `OPENROUTER_API_KEY` | API key for AI services | `sk-or-v1-...` |
| `FIELD_ENCRYPTION_KEY` | Encryption key for sensitive data | `32-character-string` |

### File Structure
```
kita-ko-v3/
├── backend/           # Django application
├── frontend/         # React application
├── Procfile          # Heroku process definitions
├── runtime.txt       # Python version
├── package.json      # Node.js configuration
└── bin/post_compile  # Build script
```

## 🛠️ Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `heroku logs --tail`
   - Ensure all dependencies are in requirements.txt
   - Verify Node.js version compatibility

2. **Static Files Not Loading**
   - Ensure WhiteNoise is configured
   - Check `STATIC_ROOT` and `STATICFILES_DIRS` settings
   - Run `heroku run python backend/manage.py collectstatic`

3. **Database Connection Issues**
   - Verify `DATABASE_URL` is set (automatic with Heroku Postgres)
   - Run migrations: `heroku run python backend/manage.py migrate`

4. **API Not Working**
   - Check CORS settings
   - Verify API base URL configuration
   - Check `ALLOWED_HOSTS` setting

### Useful Commands

```bash
# Check app status
heroku ps

# View logs
heroku logs --tail

# Run shell
heroku run python backend/manage.py shell

# Restart app
heroku restart

# Scale dynos
heroku ps:scale web=1
```

## 📱 Frontend Configuration

The React app automatically detects the environment:
- **Development**: Uses `http://localhost:8000/api`
- **Production**: Uses relative `/api` (same domain)

No additional frontend configuration needed!

## 🔒 Security Considerations

1. Use environment variables for all secrets
2. Enable HTTPS in production (automatic on Heroku)
3. Configure proper CORS settings
4. Use strong encryption keys
5. Set DEBUG=False in production

## 📊 Monitoring

- Use `heroku logs --tail` to monitor application
- Set up log drains for persistent logging
- Monitor database performance with Heroku Postgres metrics
- Consider adding error tracking (e.g., Sentry)

## 🚀 Next Steps

After successful deployment:
1. Test all functionality
2. Set up monitoring and logging
3. Configure custom domain (optional)
4. Set up CI/CD pipeline
5. Configure file storage for production uploads

---

**Need Help?** Check the logs first: `heroku logs --tail`
