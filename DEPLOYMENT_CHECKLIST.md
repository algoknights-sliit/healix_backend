# ✅ Render Deployment Checklist

Use this checklist before deploying to Render.

## 📝 Pre-Deployment

- [ ] Code is pushed to GitHub repository
- [ ] `.env` and `key.json` are in `.gitignore` (NOT committed)
- [ ] All dependencies are in `requirements.txt`
- [ ] Windows-specific packages removed (pywin32)
- [ ] `Procfile` created
- [ ] `runtime.txt` created
- [ ] `render.yaml` created (optional, for infrastructure-as-code)

## 🔐 Secrets Prepared

Have these ready to paste into Render dashboard:

### Application
- [ ] `APP_NAME=Healix_Backend`
- [ ] `ENV=production`

### Database
- [ ] `DATABASE_URL` (Supabase PostgreSQL connection string)
- [ ] `SUPABASE_URL` (https://YOUR_PROJECT.supabase.co)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` (from Supabase settings)

### Google Cloud
- [ ] `PROJECT_ID` (e.g., healix-vision-test)
- [ ] `GCS_BUCKET` (e.g., healix-test-bucket)
- [ ] `DOCAI_LOCATION` (e.g., us)
- [ ] `DOCAI_PROCESSOR_ID` (your Document AI processor)
- [ ] `GOOGLE_APPLICATION_CREDENTIALS_JSON` (copy entire key.json content)

## 🌐 Render Configuration

- [ ] Create new Web Service on Render
- [ ] Connect GitHub repository
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
- [ ] Add all environment variables
- [ ] Choose appropriate plan (Free or Paid)

## 🚀 Post-Deployment

- [ ] Check build logs for errors
- [ ] Visit `/docs` endpoint to verify API is running
- [ ] Test patient registration endpoint
- [ ] Test report upload endpoint
- [ ] Verify Google Cloud Storage connection
- [ ] Verify Supabase database connection
- [ ] Update frontend to use production API URL

## 🔧 Optional Enhancements

- [ ] Add custom domain
- [ ] Set up health check endpoint
- [ ] Configure auto-deploy from GitHub
- [ ] Set up monitoring/alerts
- [ ] Enable backup strategy

## 📊 Quick Test Commands

Once deployed, test with:

```bash
# Replace YOUR_APP with your actual Render app name
export API_URL="https://YOUR_APP.onrender.com"

# 1. Check API docs
curl $API_URL/docs

# 2. Register a test patient
curl -X POST $API_URL/api/v1/patients/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123",
    "nic": "199512345678"
  }'

# 3. Login
curl -X POST $API_URL/api/v1/patients/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

## 🐛 Common Issues

### Build Fails
- Check Python version in `runtime.txt`
- Verify all dependencies in `requirements.txt`
- Check for syntax errors in code

### App Crashes
- Missing environment variables
- Database connection string incorrect
- Google credentials not set properly

### Slow Response (Free Tier)
- Cold start (first request after inactivity)
- Normal for free tier, upgrade to fix

---

**Ready to deploy?** Follow the detailed guide in `RENDER_DEPLOYMENT.md`
