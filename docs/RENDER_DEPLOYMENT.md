# 🚀 Healix Backend - Render Deployment Guide

This guide will walk you through deploying your Healix backend to Render.

## 📋 Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Google Cloud Service Account Key** - Your `key.json` file
4. **Supabase Account** - With your database already set up

---

## 🔧 Step 1: Prepare Your Repository

### 1.1 Push Your Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Add your remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### 1.2 Update `.gitignore`

**IMPORTANT**: Make sure your `.gitignore` includes:

```
.env
key.json
venv/
__pycache__/
*.pyc
```

**Never commit** your `.env` or `key.json` files to GitHub!

---

## 🌐 Step 2: Create Web Service on Render

### 2.1 Connect to Render

1. Go to [render.com/dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your repository: `YOUR_USERNAME/Healix_Backend`

### 2.2 Configure Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `healix-backend` |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT` |
| **Plan** | Free (or paid if needed) |

---

## 🔐 Step 3: Configure Environment Variables

In the Render dashboard, go to **Environment** section and add these variables:

### Application Settings
```
APP_NAME=Healix_Backend
ENV=production
```

### Database Configuration
```
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/healix
```
*Replace with your actual Supabase connection string*

### Supabase Configuration
```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY
```

### Google Cloud Configuration
```
PROJECT_ID=healix-vision-test
GCS_BUCKET=healix-test-bucket
DOCAI_LOCATION=us
DOCAI_PROCESSOR_ID=YOUR_PROCESSOR_ID
```

### Google Service Account Key

**Option A: Using Environment Variable (Recommended)**

1. Copy the entire content of your `key.json` file
2. Add a new environment variable:
   ```
   Key: GOOGLE_APPLICATION_CREDENTIALS_JSON
   Value: [Paste entire JSON content here]
   ```

3. Update your `app/core/cloud.py` to handle this:

```python
import os
import json

# In your cloud.py or config.py
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if credentials_json:
    # Write to temp file
    with open("/tmp/key.json", "w") as f:
        f.write(credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/key.json"
else:
    # For local development
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
```

**Option B: Using Render Secret Files**

1. In Render dashboard, go to **"Secret Files"**
2. Add a new secret file:
   - **Filename**: `key.json`
   - **Contents**: Paste your entire `key.json` content
3. This will be available at `/etc/secrets/key.json` in your app

Then set:
```
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/key.json
```

---

## 🚀 Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start your application with the specified command

3. Monitor the deployment logs in real-time

---

## ✅ Step 5: Verify Deployment

Once deployed, you'll get a URL like: `https://healix-backend.onrender.com`

### Test Your API

```bash
# Health check
curl https://healix-backend.onrender.com/docs

# Test an endpoint
curl -X POST https://healix-backend.onrender.com/api/v1/patients/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123",
    "nic": "199512345678"
  }'
```

---

## 🔄 Continuous Deployment

Render automatically deploys when you push to your GitHub repository:

```bash
# Make changes to your code
git add .
git commit -m "Update feature X"
git push

# Render will automatically redeploy!
```

---

## ⚠️ Important Notes

### Free Tier Limitations

- **Cold starts**: Service spins down after 15 minutes of inactivity
- **First request slow**: May take 30-60 seconds to wake up
- **750 hours/month**: Free tier limit

### Upgrade for Production

Consider upgrading to a paid plan ($7/month) for:
- ✅ No cold starts
- ✅ Always-on service
- ✅ Better performance
- ✅ Custom domains

---

## 🐛 Troubleshooting

### Build Fails

**Check logs for:**
- Missing dependencies in `requirements.txt`
- Python version compatibility issues
- Syntax errors

**Solution:**
```bash
# Test locally first
pip install -r requirements.txt
python -m pytest  # if you have tests
```

### Application Crashes on Start

**Common issues:**
- Missing environment variables
- Database connection string incorrect
- Google credentials not set

**Check:**
1. All environment variables are set correctly
2. Database URL is accessible from Render
3. Google Cloud credentials are valid

### Database Connection Issues

**Render Free tier doesn't have static IPs**, so:
- Make sure your Supabase allows connections from any IP
- Or use Supabase connection pooler

---

## 📊 Monitoring

### View Logs
1. Go to Render dashboard
2. Select your service
3. Click **"Logs"** tab
4. Real-time logs of your application

### Metrics
- **CPU usage**
- **Memory usage**
- **Request counts**
- **Response times**

---

## 🔒 Security Best Practices

1. **Never commit secrets** to your repository
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** (Render does this automatically)
4. **Update CORS origins** in production:
   ```python
   # In app/main.py
   allow_origins=[
       "https://yourdomain.com",
       "https://www.yourdomain.com"
   ]
   ```

---

## 🎯 Next Steps

1. **Custom Domain**: Add your own domain in Render settings
2. **Database Backups**: Set up automated Supabase backups
3. **Monitoring**: Set up alerts for downtime
4. **CI/CD**: Add GitHub Actions for automated testing

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

## 🎉 Success!

Your Healix backend is now live and accessible worldwide! 🌍

**API Documentation**: `https://YOUR_APP.onrender.com/docs`

---

*Last updated: February 2026*
