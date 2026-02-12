# 🚀 ScholarPulse - Quick Start Guide

## For Developers

### First Time Setup (5 minutes)

```bash
# 1. Clone and enter directory
git clone <your-repo-url>
cd ScholarPulse

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# 4. Test API connection
python test_groq_api.py

# 5. Initialize database
python backend/manage.py migrate

# 6. Run the app
start_scholarpulse.bat
```

### Daily Development

```bash
# Start backend
python backend/manage.py runserver

# Start frontend (new terminal)
streamlit run frontend/app.py
```

Access at:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

---

## For DevOps / Deployment

### Deploy to Render (Backend)

1. **Push to GitHub:**
```bash
git push origin main
```

2. **Render Configuration:**
   - Build: `pip install -r requirements.txt && python backend/manage.py migrate`
   - Start: `gunicorn scholarpulse.wsgi --chdir backend --bind 0.0.0.0:$PORT`

3. **Environment Variables:**
   ```
   GROQ_API_KEY=<your-key>
   DJANGO_SECRET_KEY=<random-key>
   DJANGO_DEBUG=False
   ```

4. **Verify:**
```bash
curl https://your-app.onrender.com/api/health/
```

### Deploy to Streamlit Cloud (Frontend)

1. **Connect Repository**
2. **Set Main File:** `frontend/app.py`
3. **Add Secret:** `SCHOLARPULSE_API_URL=https://your-backend.onrender.com`
4. **Deploy**

---

## Troubleshooting

### Problem: Groq API Error

```bash
# Test API locally
python test_groq_api.py

# Check production
python debug_production.py
```

### Problem: Empty Results

1. Check Render logs
2. Verify API key has credits
3. Test model name is correct: `llama-3.3-70b-versatile`

### Problem: Frontend Can't Connect

1. Verify `SCHOLARPULSE_API_URL` in Streamlit secrets
2. Check backend is running (not sleeping)
3. Test health endpoint

---

## Key Files

- `config.py` - Model and API configuration
- `agent/llm.py` - LLM client with retry logic
- `.env` - Your API keys (never commit!)
- `test_groq_api.py` - API diagnostic tool
- `debug_production.py` - Production debugging

---

## Getting Help

1. **Check logs:**
   - Local: Terminal output
   - Render: Dashboard → Logs
   - Streamlit: App → Logs

2. **Run diagnostics:**
   ```bash
   python test_groq_api.py
   python debug_production.py
   ```

3. **Review documentation:**
   - `README.md` - Full documentation
   - `DEPLOYMENT_CHECKLIST.md` - Deployment guide
   - `FIX_SUMMARY.md` - Recent fixes

---

## API Keys

Get your keys from:
- Groq: https://console.groq.com/keys
- Gemini: https://makersuite.google.com/app/apikey
- Serper: https://serper.dev

---

## Common Commands

```bash
# Test Groq API
python test_groq_api.py

# Debug production
python debug_production.py

# Run migrations
python backend/manage.py migrate

# Create superuser
python backend/manage.py createsuperuser

# Collect static files
python backend/manage.py collectstatic

# Run tests
python -m pytest
```

---

**Need more help?** Check `README.md` for detailed documentation.
