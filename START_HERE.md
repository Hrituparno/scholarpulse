# 🚀 START HERE - ScholarPulse Deployment

Quick reference for deploying your AI Research Agent to production.

---

## 📁 Important Files

### Deployment
- **`DEPLOYMENT.md`** ← Read this for full deployment guide
- **`DEPLOY_CHECKLIST.md`** ← Use this while deploying
- **`render.yaml`** ← Render configuration (auto-used)
- **`.streamlit/config.toml`** ← Streamlit configuration (auto-used)

### Documentation
- **`README.md`** ← Project overview
- **`PORTFOLIO_READY.md`** ← What's ready for your portfolio
- **`CHANGELOG.md`** ← Version history

### Development
- **`run_local.bat`** ← Test locally before deploying
- **`.env.example`** ← Copy to `.env` and add your API keys

---

## ⚡ Quick Deploy (25 minutes)

### 1. Push to GitHub (5 min)
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy Backend (10 min)
1. Go to https://render.com
2. Sign up with GitHub
3. New Web Service → Connect repository
4. Name: `scholarpulse-backend`
5. Build: `cd backend && pip install -r ../requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
6. Start: `cd backend && gunicorn scholarpulse.wsgi:application --bind 0.0.0.0:$PORT`
7. Add environment variables (see DEPLOYMENT.md)
8. Deploy!

### 3. Deploy Frontend (5 min)
1. Go to https://share.streamlit.io
2. Sign up with GitHub
3. New app → Select repository
4. Main file: `frontend/app.py`
5. Add env var: `SCHOLARPULSE_API_URL` = your Render URL
6. Deploy!

### 4. Test (5 min)
1. Visit your Streamlit URL
2. Submit a test query
3. Verify results
4. Add to portfolio!

---

## 🎯 Your URLs

After deployment, you'll have:

**Live Demo:**
```
https://scholarpulse.streamlit.app
```

**Backend API:**
```
https://scholarpulse-backend.onrender.com
```

Add these to your portfolio/resume!

---

## 🧪 Test Locally First

Before deploying:

```bash
# 1. Add API keys to .env
cp .env.example .env
# Edit .env with your keys

# 2. Run locally
run_local.bat

# 3. Test at http://localhost:8501
```

---

## 📚 Need Help?

- **Full Guide:** `DEPLOYMENT.md`
- **Checklist:** `DEPLOY_CHECKLIST.md`
- **Portfolio Info:** `PORTFOLIO_READY.md`

---

## ✅ What's Ready

- ✅ Code cleaned up
- ✅ Production configured
- ✅ Documentation complete
- ✅ Ready to deploy

---

**Next Step:** Read `DEPLOYMENT.md` and start deploying! 🚀
