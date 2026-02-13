# ✅ Deployment Checklist

Use this checklist to deploy ScholarPulse to production.

---

## 📋 Pre-Deployment

- [ ] All code committed to GitHub
- [ ] `.env` file NOT committed (in `.gitignore`)
- [ ] API keys ready (Groq, Gemini, Oxlo)
- [ ] Tested locally and everything works
- [ ] Requirements.txt up to date

---

## 🖥️ Backend Deployment (Render)

### Account Setup
- [ ] Created Render account
- [ ] Connected GitHub account
- [ ] Repository access granted

### Service Configuration
- [ ] Created new Web Service
- [ ] Selected correct repository
- [ ] Set name: `scholarpulse-backend`
- [ ] Selected region: Oregon (free tier)
- [ ] Set branch: `main`

### Build Configuration
- [ ] Build command:
  ```
  cd backend && pip install -r ../requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
  ```
- [ ] Start command:
  ```
  cd backend && gunicorn scholarpulse.wsgi:application --bind 0.0.0.0:$PORT
  ```

### Environment Variables
- [ ] `SECRET_KEY` - Generated random string
- [ ] `DEBUG` - Set to `False`
- [ ] `ALLOWED_HOSTS` - Set to `.onrender.com`
- [ ] `GROQ_API_KEY` - Your Groq API key
- [ ] `GOOGLE_API_KEY` - Your Gemini API key
- [ ] `OXLO_API_KEY` - Your Oxlo API key
- [ ] `PYTHON_VERSION` - Set to `3.11.0`

### Deployment
- [ ] Clicked "Create Web Service"
- [ ] Waited for deployment (5-10 minutes)
- [ ] Got backend URL: `https://scholarpulse-backend.onrender.com`

### Testing
- [ ] Visited `/api/health/` endpoint
- [ ] Received `{"status": "healthy"}` response
- [ ] No errors in Render logs

---

## 🎨 Frontend Deployment (Streamlit Cloud)

### Account Setup
- [ ] Created Streamlit Cloud account
- [ ] Connected GitHub account
- [ ] Repository access granted

### App Configuration
- [ ] Clicked "New app"
- [ ] Selected repository: `scholarpulse`
- [ ] Set main file: `frontend/app.py`
- [ ] Set branch: `main`

### Environment Variables
- [ ] `SCHOLARPULSE_API_URL` - Your Render backend URL
  ```
  https://scholarpulse-backend.onrender.com
  ```

### Deployment
- [ ] Clicked "Deploy!"
- [ ] Waited for deployment (2-3 minutes)
- [ ] Got frontend URL: `https://scholarpulse.streamlit.app`

### Testing
- [ ] Visited Streamlit URL
- [ ] UI loads correctly
- [ ] Submitted test research query
- [ ] Received results (papers, ideas, report)
- [ ] No errors in browser console

---

## 🔄 Post-Deployment

### Verification
- [ ] Backend health check passes
- [ ] Frontend connects to backend
- [ ] Research queries work end-to-end
- [ ] All LLM providers working
- [ ] Error handling works correctly

### Documentation
- [ ] Updated README with live demo URL
- [ ] Added URLs to portfolio/resume
- [ ] Documented any deployment issues

### Monitoring
- [ ] Set up UptimeRobot (optional - keeps backend awake)
- [ ] Bookmarked Render dashboard
- [ ] Bookmarked Streamlit dashboard

---

## 🎯 URLs to Save

**Live Demo:**
```
https://scholarpulse.streamlit.app
```

**Backend API:**
```
https://scholarpulse-backend.onrender.com
```

**GitHub Repository:**
```
https://github.com/yourusername/scholarpulse
```

**Render Dashboard:**
```
https://dashboard.render.com
```

**Streamlit Dashboard:**
```
https://share.streamlit.io
```

---

## 🆘 Troubleshooting

### Backend Not Starting
- [ ] Check build logs in Render
- [ ] Verify all environment variables set
- [ ] Check requirements.txt has all dependencies
- [ ] Verify build/start commands are correct

### Frontend Can't Connect
- [ ] Verify `SCHOLARPULSE_API_URL` is correct
- [ ] Check backend is running (visit /api/health/)
- [ ] Check CORS settings in backend
- [ ] Check Streamlit logs for errors

### API Errors
- [ ] Verify API keys are correct
- [ ] Check no extra spaces in keys
- [ ] Test keys locally first
- [ ] Check API provider status pages

---

## 📊 Success Criteria

- ✅ Backend responds to health checks
- ✅ Frontend loads without errors
- ✅ Can submit research queries
- ✅ Receives papers from arXiv
- ✅ Generates ideas successfully
- ✅ Creates complete reports
- ✅ All LLM providers working
- ✅ Error handling works
- ✅ Auto-deploy from GitHub works

---

## 🎉 Deployment Complete!

Once all checkboxes are checked, your app is live and ready to share!

**Next Steps:**
1. Add live demo URL to your portfolio
2. Share with potential employers
3. Monitor logs for any issues
4. Iterate and improve based on feedback

---

**Congratulations! Your ScholarPulse is now production-ready! 🚀**
