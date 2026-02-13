# 🚀 ScholarPulse - Production Deployment Guide

Deploy ScholarPulse to Render (Backend) + Streamlit Cloud (Frontend) for a professional, always-on portfolio project.

---

## 🎯 What You'll Get

- **Professional URLs:**
  - Backend: `https://scholarpulse-backend.onrender.com`
  - Frontend: `https://scholarpulse.streamlit.app`
- **Always Online:** 24/7 availability
- **No Manual Start:** Deploys automatically from GitHub
- **Free Tier:** Both platforms offer free hosting
- **Portfolio Ready:** Perfect for showing to companies

---

## 📋 Prerequisites

1. **GitHub Account** - To host your code
2. **Render Account** - For backend (free)
3. **Streamlit Cloud Account** - For frontend (free)
4. **API Keys** - Groq, Gemini, Oxlo

---

## 🔧 Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

Make sure your repository is public or you have access to connect it to Render/Streamlit.

---

## 🖥️ Step 2: Deploy Backend to Render

### 2.1 Create Render Account
1. Go to: https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 2.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your `scholarpulse` repository

### 2.3 Configure Service

**Basic Settings:**
- **Name:** `scholarpulse-backend`
- **Region:** Oregon (US West) - Free tier
- **Branch:** `main`
- **Root Directory:** Leave empty
- **Runtime:** Python 3
- **Build Command:**
  ```bash
  cd backend && pip install -r ../requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
  ```
- **Start Command:**
  ```bash
  cd backend && gunicorn scholarpulse.wsgi:application --bind 0.0.0.0:$PORT
  ```

**Environment Variables:**
Click **"Advanced"** → **"Add Environment Variable"**

Add these:
```
SECRET_KEY = [Generate Random String]
DEBUG = False
ALLOWED_HOSTS = .onrender.com
GROQ_API_KEY = [Your Groq API Key]
GOOGLE_API_KEY = [Your Gemini API Key]
OXLO_API_KEY = [Your Oxlo API Key]
PYTHON_VERSION = 3.11.0
```

### 2.4 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first deployment
3. You'll get a URL like: `https://scholarpulse-backend.onrender.com`

### 2.5 Test Backend
Visit: `https://scholarpulse-backend.onrender.com/api/health/`

You should see: `{"status": "healthy"}`

---

## 🎨 Step 3: Deploy Frontend to Streamlit Cloud

### 3.1 Create Streamlit Account
1. Go to: https://share.streamlit.io
2. Sign up with GitHub
3. Authorize Streamlit

### 3.2 Deploy App
1. Click **"New app"**
2. Select your repository: `scholarpulse`
3. **Main file path:** `frontend/app.py`
4. **Branch:** `main`
5. Click **"Advanced settings"**

### 3.3 Configure Environment Variables

Add this variable:
```
SCHOLARPULSE_API_URL = https://scholarpulse-backend.onrender.com
```

Replace with your actual Render backend URL!

### 3.4 Deploy
1. Click **"Deploy!"**
2. Wait 2-3 minutes
3. You'll get a URL like: `https://scholarpulse.streamlit.app`

---

## ✅ Step 4: Verify Deployment

### 4.1 Test Backend
```bash
curl https://scholarpulse-backend.onrender.com/api/health/
```

Should return: `{"status": "healthy"}`

### 4.2 Test Frontend
1. Visit your Streamlit URL
2. Enter a research query
3. Submit and wait for results
4. Verify papers, ideas, and report are generated

---

## 🔄 Step 5: Auto-Deploy Setup

Both platforms auto-deploy when you push to GitHub!

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Render and Streamlit will automatically redeploy!
```

---

## 🎯 URLs for Your Portfolio

Add these to your resume/portfolio:

**Live Demo:**
```
https://scholarpulse.streamlit.app
```

**GitHub Repository:**
```
https://github.com/yourusername/scholarpulse
```

**API Documentation:**
```
https://scholarpulse-backend.onrender.com/api/
```

---

## 🆘 Troubleshooting

### Backend Issues

**"Application failed to start"**
- Check build logs in Render dashboard
- Verify all environment variables are set
- Make sure `requirements.txt` has all dependencies

**"502 Bad Gateway"**
- Backend is starting (wait 2-3 minutes on free tier)
- Check if service is sleeping (free tier sleeps after 15 min inactivity)

**"Database error"**
- Run migrations: Add to build command: `python manage.py migrate`

### Frontend Issues

**"Cannot connect to backend"**
- Verify `SCHOLARPULSE_API_URL` environment variable
- Check backend is running: visit `/api/health/`
- Check CORS settings in backend

**"Module not found"**
- Verify `requirements.txt` has all dependencies
- Redeploy from Streamlit dashboard

### API Key Issues

**"API key invalid"**
- Check environment variables in Render dashboard
- Make sure no extra spaces in API keys
- Verify keys are valid by testing locally first

---

## 💡 Pro Tips

### 1. Keep Backend Awake (Free Tier)
Free tier sleeps after 15 minutes of inactivity. Options:
- Use a service like UptimeRobot to ping every 14 minutes
- Upgrade to paid tier ($7/month) for always-on

### 2. Monitor Logs
- **Render:** Dashboard → Logs tab
- **Streamlit:** Click "Manage app" → Logs

### 3. Custom Domain (Optional)
Both platforms support custom domains:
- Render: Settings → Custom Domain
- Streamlit: Settings → Custom Domain

### 4. Database Persistence
Current setup uses SQLite (resets on redeploy). For production:
- Add PostgreSQL database in Render
- Update `settings.py` database config
- Run migrations

---

## 📊 Cost Breakdown

**Free Tier (Current Setup):**
- Render Backend: $0/month (with limitations)
- Streamlit Frontend: $0/month
- **Total: $0/month**

**Paid Tier (Recommended for Portfolio):**
- Render Backend: $7/month (always-on, faster)
- Streamlit Frontend: $0/month
- **Total: $7/month**

---

## 🎓 For Your Portfolio

When showing to companies, mention:
- ✅ Full-stack deployment (Django + Streamlit)
- ✅ CI/CD pipeline (auto-deploy from GitHub)
- ✅ RESTful API design
- ✅ Multi-LLM integration
- ✅ Production-ready configuration
- ✅ Environment-based configuration
- ✅ Error handling and logging

---

## 📞 Need Help?

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com

**Streamlit Support:**
- Docs: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io

---

**Your app is now live and portfolio-ready! 🎉**

Share your Streamlit URL with companies and watch the magic happen!
