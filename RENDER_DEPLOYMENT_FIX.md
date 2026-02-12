# 🔧 Render Deployment Fix - Force Fresh Deploy

**Issue:** Render is still using old Groq model `llama3-70b-8192` despite code update  
**Cause:** Cached deployment or environment variable override  
**Solution:** Force fresh deployment and verify environment variables

---

## 🚨 CRITICAL: The Problem

Your Render logs show:
```
LLM generation failed (groq): Error code: 400 - 
{'error': {'message': 'The model 'llama3-70b-8192' has been decommissioned'}}
```

This means Render is NOT using the updated code from GitHub!

---

## ✅ SOLUTION: Force Fresh Deployment

### Step 1: Clear Build Cache on Render

1. Go to: https://dashboard.render.com/
2. Select your **scholarpulse** backend service
3. Click **Manual Deploy** → **Clear build cache & deploy**
4. Wait 3-5 minutes for fresh deployment

**Why this works:** Clears any cached Python packages or old code

### Step 2: Verify Environment Variables

1. In Render dashboard, go to your service
2. Click **Environment** tab
3. **CHECK FOR:** Any variable named `GROQ_MODEL`
4. **IF EXISTS:** Delete it or update to `llama-3.3-70b-versatile`
5. Click **Save Changes**

**Why this matters:** Environment variables override config.py

### Step 3: Verify GitHub Code is Latest

1. Go to: https://github.com/Hrituparno/scholarpulse
2. Open `config.py`
3. Verify line 14 shows:
   ```python
   GROQ_MODEL = "llama-3.3-70b-versatile"
   ```
4. If not, the push didn't work - re-push the code

### Step 4: Trigger Manual Deploy

1. In Render dashboard
2. Click **Manual Deploy** → **Deploy latest commit**
3. Watch the logs for:
   ```
   ✓ Building...
   ✓ Installing dependencies...
   ✓ Starting service...
   ✓ Live
   ```

### Step 5: Verify Deployment Success

**Check Render Logs for:**
```
✅ Multi-LLM initialized: Groq=True, Gemini=True, Oxlo=True
✅ [LLM] Using Groq (model: llama-3.3-70b-versatile)
✅ [LLM] Groq success
```

**Should NOT see:**
```
❌ Model 'llama3-70b-8192' has been decommissioned
❌ Model 'llama-3.1-8b-instant' not found
```

---

## 🔍 Troubleshooting

### Issue: Still seeing old model error

**Possible causes:**
1. Environment variable `GROQ_MODEL` is set on Render (overrides code)
2. Build cache not cleared
3. Wrong branch deployed (not `main`)
4. GitHub webhook not triggering

**Fix:**
```bash
# Option 1: Force push to trigger webhook
git commit --allow-empty -m "Force Render redeploy"
git push origin main

# Option 2: Manual deploy with cache clear (recommended)
# Use Render dashboard: Manual Deploy → Clear build cache & deploy
```

### Issue: Deployment fails

**Check:**
1. Render logs for Python errors
2. requirements.txt has all dependencies
3. Start command is correct: `gunicorn backend.scholarpulse.wsgi:application`
4. Python version matches (3.11+)

### Issue: Service starts but still errors

**Check:**
1. All API keys are set in Render environment:
   - `GROQ_API_KEY`
   - `GOOGLE_API_KEY`
   - `OXLO_API_KEY`
   - `SERPER_API_KEY`
2. No typos in environment variable names
3. API keys are valid and not expired

---

## 📋 Complete Render Environment Variables Checklist

Your Render service should have these environment variables:

```bash
# Required API Keys
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
OXLO_API_KEY=sk_...
SERPER_API_KEY=...

# Django Settings
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com

# Optional (DO NOT SET - let config.py handle it)
# GROQ_MODEL=llama-3.3-70b-versatile  # ❌ DELETE THIS IF IT EXISTS
# GEMINI_MODEL=gemini-2.0-flash       # ❌ DELETE THIS IF IT EXISTS
```

**IMPORTANT:** Do NOT set `GROQ_MODEL` or `GEMINI_MODEL` as environment variables on Render. Let `config.py` handle model selection.

---

## 🎯 Expected Results After Fix

### Render Logs Should Show:

```
INFO 2026-02-12 05:13:45,581 [agent_service] Multi-LLM initialized: Groq=True, Gemini=True, Oxlo=True
INFO 2026-02-12 05:13:45,582 [llm] Groq initialized: llama-3.3-70b-versatile
INFO 2026-02-12 05:13:45,583 [llm] Gemini initialized: gemini-2.0-flash
INFO 2026-02-12 05:13:45,584 [llm] Oxlo initialized: llama-3.1-70b
INFO 2026-02-12 05:13:46,123 [llm] [LLM] Using Groq for generation (model: llama-3.3-70b-versatile)
INFO 2026-02-12 05:13:47,456 [llm] [LLM] Groq success - 384 chars
INFO 2026-02-12 05:13:48,789 [llm] [LLM] Batch generation complete: 5/5 successful
```

### Frontend Should Work:

1. Open: https://hrituparno-scholarpulse-app-nya41k.streamlit.app/
2. Submit query: "machine learning optimization"
3. See:
   - ✅ Papers loading
   - ✅ Ideas generated
   - ✅ Report sections complete
   - ✅ No "Mission Failed" error
   - ✅ Response time 15-30s

---

## 🚀 Quick Fix Commands

### Option 1: Force Redeploy via Git (Fastest)

```bash
# Create empty commit to trigger webhook
git commit --allow-empty -m "Force Render redeploy with updated Groq model"
git push origin main

# Wait 3-5 minutes, then check Render logs
```

### Option 2: Manual Deploy via Dashboard (Most Reliable)

1. https://dashboard.render.com/
2. Select **scholarpulse** service
3. Click **Manual Deploy**
4. Select **Clear build cache & deploy**
5. Wait 3-5 minutes
6. Check logs for new model

### Option 3: Delete and Recreate Service (Nuclear Option)

**Only if above options fail:**

1. Export all environment variables from Render
2. Delete the service
3. Create new service from GitHub
4. Re-add all environment variables
5. Deploy

---

## ✅ Verification Checklist

After deployment:

- [ ] Render logs show `llama-3.3-70b-versatile` (not old model)
- [ ] No "model decommissioned" errors
- [ ] No "JSONDecodeError" errors
- [ ] Frontend loads without "Mission Failed"
- [ ] Research queries return results
- [ ] Response time is 15-30 seconds
- [ ] Papers show (5 papers)
- [ ] Ideas show (5 ideas)
- [ ] Report sections complete

---

## 📞 Next Steps

1. **Immediately:** Go to Render dashboard
2. **Clear cache:** Manual Deploy → Clear build cache & deploy
3. **Wait 5 min:** Let deployment complete
4. **Check logs:** Verify new model in use
5. **Test frontend:** Submit a research query
6. **Verify:** No errors, results returned

---

**Status:** 🔴 URGENT - Render needs fresh deployment  
**Action Required:** Clear build cache and redeploy NOW  
**Expected Time:** 5 minutes to fix

