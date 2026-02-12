# 🚀 ScholarPulse Deployment Checklist

## Pre-Deployment Testing

### Local Environment
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file configured with valid API keys
- [ ] Groq API test passes: `python test_groq_api.py`
- [ ] Database migrations applied: `python backend/manage.py migrate`
- [ ] Backend runs without errors: `python backend/manage.py runserver`
- [ ] Frontend connects to backend: `streamlit run frontend/app.py`
- [ ] Test search query works end-to-end

### Code Quality
- [ ] No hardcoded API keys in code
- [ ] `.env` file is in `.gitignore`
- [ ] All sensitive data removed from logs
- [ ] Error handling added for all API calls
- [ ] Logging configured for production

## Backend Deployment (Render)

### Repository Setup
- [ ] Code pushed to GitHub
- [ ] `.env` file NOT committed
- [ ] `.env.example` file committed
- [ ] `requirements.txt` up to date

### Render Configuration
- [ ] New Web Service created
- [ ] Repository connected
- [ ] Build command set: `pip install -r requirements.txt && python backend/manage.py migrate`
- [ ] Start command set: `gunicorn scholarpulse.wsgi --chdir backend --bind 0.0.0.0:$PORT`
- [ ] Python version: 3.9+

### Environment Variables (Render)
- [ ] `GROQ_API_KEY` - Your Groq API key
- [ ] `DJANGO_SECRET_KEY` - Random secret key (generate new one!)
- [ ] `DJANGO_DEBUG` - Set to `False`
- [ ] `GOOGLE_API_KEY` - (Optional) Gemini fallback
- [ ] `SERPER_API_KEY` - (Optional) Web search
- [ ] `SCHOLARPULSE_OUTPUT_DIR` - `/opt/render/project/src/output`

### Deployment Verification
- [ ] Build completes successfully
- [ ] No errors in deployment logs
- [ ] Health check endpoint works: `https://your-app.onrender.com/api/health/`
- [ ] Test API call succeeds (see README for curl command)
- [ ] No Groq API errors in logs
- [ ] Response times acceptable

## Frontend Deployment (Streamlit Cloud)

### Streamlit Configuration
- [ ] App created on Streamlit Cloud
- [ ] Repository connected
- [ ] Main file path: `frontend/app.py`
- [ ] Python version: 3.9+

### Secrets Configuration
- [ ] `SCHOLARPULSE_API_URL` set to Render backend URL
- [ ] URL format: `https://your-backend.onrender.com` (no trailing slash)

### Deployment Verification
- [ ] App deploys successfully
- [ ] No import errors
- [ ] Frontend loads without errors
- [ ] Can connect to backend API
- [ ] Test search query works
- [ ] Results display correctly

## Post-Deployment Testing

### Functional Tests
- [ ] Submit research query
- [ ] Papers are fetched successfully
- [ ] LLM analysis completes
- [ ] Ideas are generated
- [ ] Report is created
- [ ] No errors in Render logs
- [ ] No errors in Streamlit logs

### Performance Tests
- [ ] Response time < 30 seconds for typical query
- [ ] No timeout errors
- [ ] Rate limiting works correctly
- [ ] Retry logic functions properly

### Error Handling
- [ ] Invalid query handled gracefully
- [ ] API key errors show helpful message
- [ ] Rate limit errors trigger backoff
- [ ] Network errors don't crash app
- [ ] Empty results handled properly

## Monitoring Setup

### Render Monitoring
- [ ] Enable email alerts for deployment failures
- [ ] Check logs regularly for errors
- [ ] Monitor API response times
- [ ] Track error rates

### Streamlit Monitoring
- [ ] Check app analytics
- [ ] Monitor user errors
- [ ] Track usage patterns

## Common Issues & Fixes

### Issue: Groq API 401 Error
**Symptoms:** Authentication failed, invalid API key
**Fix:**
1. Verify GROQ_API_KEY in Render environment variables
2. Get new key from https://console.groq.com/keys
3. Redeploy after updating

### Issue: Model Not Found
**Symptoms:** Model 'llama3-70b-8192' not found
**Fix:**
1. Update config.py: `GROQ_MODEL = "llama-3.3-70b-versatile"`
2. Commit and push changes
3. Redeploy

### Issue: Rate Limit (429)
**Symptoms:** Too many requests error
**Fix:**
1. Wait 1-2 minutes
2. Retry logic should handle automatically
3. Consider upgrading Groq plan

### Issue: Frontend Can't Connect
**Symptoms:** Network error, CORS error
**Fix:**
1. Verify SCHOLARPULSE_API_URL in Streamlit secrets
2. Check backend is running (not sleeping)
3. Verify CORS settings in Django settings.py

### Issue: Empty Responses
**Symptoms:** No papers found, no ideas generated
**Fix:**
1. Check Render logs for detailed errors
2. Verify API key has credits
3. Test locally with test_groq_api.py
4. Check LLM provider status

## Security Checklist

- [ ] No API keys in code
- [ ] No API keys in logs
- [ ] DJANGO_DEBUG=False in production
- [ ] DJANGO_SECRET_KEY is unique and random
- [ ] CORS configured correctly
- [ ] HTTPS enabled (automatic on Render/Streamlit)
- [ ] Rate limiting configured

## Documentation

- [ ] README.md updated with deployment instructions
- [ ] .env.example includes all required variables
- [ ] API documentation up to date
- [ ] Troubleshooting guide complete

## Final Sign-Off

- [ ] All tests passing
- [ ] No errors in production logs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Team notified of deployment

---

**Deployment Date:** _____________

**Deployed By:** _____________

**Backend URL:** _____________

**Frontend URL:** _____________

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________
