# Changelog

All notable changes to ScholarPulse will be documented in this file.

## [3.0.0] - 2026-02-13

### 🚀 Major: Production Deployment Configuration

#### Changed
- **BREAKING:** Switched from localhost to production deployment architecture
- Frontend now defaults to Render backend URL instead of localhost
- Removed all localhost/tunnel related infrastructure

#### Added
- `render.yaml` - Render deployment configuration
- `DEPLOYMENT.md` - Complete production deployment guide
- `DEPLOY_CHECKLIST.md` - Step-by-step deployment checklist
- `.streamlit/config.toml` - Streamlit Cloud theme configuration
- `run_local.bat` - Local development script for testing

#### Removed
- All Cloudflare tunnel scripts and executables
- Localhost startup scripts
- Tunnel setup guides and documentation
- Unnecessary localhost-specific files

#### Fixed
- Frontend API client properly configured for production
- Environment variable handling for different deployment environments
- CORS configuration optimized for Streamlit Cloud

### 📦 Deployment Ready
- Backend: Configured for Render with Gunicorn
- Frontend: Configured for Streamlit Cloud
- Auto-deploy from GitHub enabled
- Production-grade error handling
- Health check endpoints

---

## [2.0.0] - 2026-02-12

### 🔧 Fixed - Critical Groq API Integration

#### Root Cause
- Deprecated Groq model name causing "model not found" errors in production
- Missing error handling and retry logic for API failures
- Insufficient logging making production debugging difficult

#### Changes

**Core LLM Integration (`agent/llm.py`)**
- ✅ Added retry logic with exponential backoff (3 attempts)
- ✅ Implemented explicit 60-second timeout
- ✅ Added response validation and null checks
- ✅ Enhanced error categorization (auth, rate limit, model errors)
- ✅ Improved logging with detailed error messages
- ✅ Smart retry logic (don't retry auth errors, longer backoff for rate limits)

**Configuration (`config.py`)**
- ✅ Updated Groq model: `llama3-70b-8192` → `llama-3.3-70b-versatile`
- ✅ Updated Gemini model: `gemini-2.5-flash` → `gemini-2.0-flash`

**Dependencies (`requirements.txt`)**
- ✅ Pinned Groq SDK to `>=0.30.0` (latest stable)
- ✅ Added version comments for clarity

**Agent Service (`backend/research/services/agent_service.py`)**
- ✅ Added LLM availability check before execution
- ✅ Better error messages for missing API keys

### 📁 Added - New Files

**Environment Configuration**
- `.env.example` - Template for environment variables with documentation

**Testing & Debugging Tools**
- `test_groq_api.py` - Comprehensive Groq API diagnostic script
- `debug_production.py` - Production debugging and health check tool

**Documentation**
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step deployment guide
- `FIX_SUMMARY.md` - Detailed analysis of fixes
- `QUICK_START.md` - Quick reference for developers
- `CHANGELOG.md` - This file

**CI/CD**
- `.github/workflows/test.yml` - GitHub Actions workflow for automated testing

### 🔒 Security

**Improved**
- ✅ API keys never logged or exposed
- ✅ `.env` properly excluded from git
- ✅ `.env.example` provided for documentation
- ✅ Production settings enforced (`DJANGO_DEBUG=False`)

### 📚 Documentation

**Updated**
- `README.md` - Enhanced with deployment instructions and troubleshooting
- `.gitignore` - Improved to exclude sensitive files and logs

**Added**
- Comprehensive deployment guide
- Production debugging instructions
- Common issues and solutions
- API key setup instructions

### 🧪 Testing

**Added**
- Automated Groq API connectivity test
- Production health check script
- GitHub Actions CI/CD pipeline
- Environment validation

### 🚀 Deployment

**Improved**
- Clear Render deployment instructions
- Streamlit Cloud setup guide
- Environment variable documentation
- Health check endpoints

### 💡 Developer Experience

**Added**
- Quick start guide for new developers
- Diagnostic tools for troubleshooting
- Detailed error messages with fix suggestions
- Automated testing scripts

---

## [1.0.0] - 2026-02-07

### Initial Release

**Features**
- Multi-agent research pipeline
- ArXiv paper search and analysis
- LLM-powered hypothesis generation
- Experiment design and evaluation
- Report generation (Markdown, DOCX, JSON)
- Django REST API backend
- Streamlit frontend
- SQLite database
- Multi-provider LLM support (Groq, Gemini, Oxlo)

**Architecture**
- Frontend: Streamlit with custom CSS
- Backend: Django REST Framework
- Database: SQLite
- LLM Providers: Groq (primary), Gemini (fallback), Oxlo (alternative)

**Deployment**
- Render.com support (backend)
- Streamlit Cloud support (frontend)
- Gunicorn WSGI server
- WhiteNoise static file serving

---

## Version History

- **2.0.0** (2026-02-12) - Production-ready with fixed Groq API integration
- **1.0.0** (2026-02-07) - Initial release

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

**Local Development:**
```bash
# 1. Pull latest code
git pull origin main

# 2. Update dependencies
pip install -r requirements.txt --upgrade

# 3. Test API connection
python test_groq_api.py

# 4. No database changes needed
```

**Production (Render):**
```bash
# 1. Push to GitHub (triggers auto-deploy)
git push origin main

# 2. Verify environment variables are set:
#    - GROQ_API_KEY
#    - DJANGO_SECRET_KEY
#    - DJANGO_DEBUG=False

# 3. Monitor deployment logs

# 4. Test health endpoint
curl https://your-app.onrender.com/api/health/

# 5. Run production diagnostics
python debug_production.py
```

**No Breaking Changes** - All existing API endpoints and functionality remain the same.

---

## Future Roadmap

### Planned for 2.1.0
- [ ] Celery integration for async task processing
- [ ] PostgreSQL migration guide
- [ ] Advanced PDF parsing and vectorization
- [ ] Multi-language support
- [ ] Enhanced caching layer

### Planned for 3.0.0
- [ ] User authentication and authorization
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Custom LLM fine-tuning support
- [ ] API rate limiting and quotas

---

## Contributing

See `README.md` for contribution guidelines.

## License

See `LICENSE` file for details.

---

**Maintained by:** ScholarPulse Team  
**Last Updated:** February 12, 2026
