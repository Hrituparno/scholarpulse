# 🚨 URGENT: Fix Render & Streamlit Deployment

**Problem:** Render is still using old Groq model causing HTTP 500 errors  
**Solution:** Force fresh deployment on both platforms

---

## 🎯 DO THIS NOW (5 Minutes Total)

### STEP 1: Fix Render Backend (3 minutes)

1. **Open Render Dashboard**
   - Go to: https://dashboard.render.com/
   - Login with your account

2. **Find Your Service**
   - Look for: **scholarpulse** (or your backend service name)
   - Click on it

3. **Clear Cache & Redeploy**
   - Click **Manual Deploy** button (top right)
   - Select **"Clear build cache & deploy"**
   - Click **Deploy**
   - ⏳ Wait 3-5 minutes

4. **Watch the Logs**
   - Click **Logs** tab
   - Wait for deployment to complete
   - Look for: `Live` status

5. **Verify Success**
   - Logs should show:
     ```
     ✅ Multi-LLM initialized: Groq=True
     ✅ Groq initialized: llama-3.3-70b-versatile
     ```
   - Should NOT show:
     ```
     ❌ Model 'llama3-70b-8192' has been decommissioned
     ```

### STEP 2: Fix Streamlit Frontend (2 minutes)

1. **Open Streamlit Dashboard**
   - Go to: https://share.streamlit.io/
   - Login with your account

2. **Find Your App**
   - Look for: **scholarpulse-app** (or your app name)
   - Click on it

3. **Reboot the App**
   - Click **⋮** (three dots menu)
   - Select **"Reboot app"**
   - ⏳ Wait 1-2 minutes

4. **Verify Success**
   - Open your app: https://hrituparno-scholarpulse-app-nya41k.streamlit.app/
   - Submit test query: "machine learning"
   - Should see results (not "Mission Failed")

---

## ✅ Success Checklist

After completing both steps:

**Render Backend:**
- [ ] Deployment shows "Live" status
- [ ] Logs show new Groq model: `llama-3.3-70b-versatile`
- [ ] No "decommissioned" errors
- [ ] Health endpoint works: https://scholarpulse.onrender.com/api/health/

**Streamlit Frontend:**
- [ ] App loads without errors
- [ ] Can submit research queries
- [ ] Results appear (papers + ideas + report)
- [ ] No "Mission Failed" error
- [ ] No "HTTP 500" error

---

## 🔍 If Still Not Working

### Check Render Environment Variables

1. In Render dashboard → Your service
2. Click **Environment** tab
3. **Look for:** `GROQ_MODEL` variable
4. **If exists:** DELETE it (let config.py handle it)
5. Click **Save Changes**
6. Redeploy again

### Force GitHub Sync

```bash
# In your local terminal
git commit --allow-empty -m "Force redeploy"
git push origin main

# Wait 3 minutes for auto-deploy
```

### Nuclear Option: Delete & Recreate

**Only if nothing else works:**

1. Export all Render environment variables (screenshot them)
2. Delete the Render service
3. Create new service from GitHub repo
4. Add back all environment variables
5. Deploy

---

## 📞 What to Do Right Now

1. ✅ Open Render dashboard
2. ✅ Click "Clear build cache & deploy"
3. ⏳ Wait 3-5 minutes
4. ✅ Open Streamlit dashboard
5. ✅ Click "Reboot app"
6. ⏳ Wait 1-2 minutes
7. ✅ Test your app

**Total time: 5-7 minutes**

---

## 🎉 Expected Result

After fix:
- ✅ Backend uses new Groq model
- ✅ No more HTTP 500 errors
- ✅ Frontend works perfectly
- ✅ Research queries return results
- ✅ Response time 15-30 seconds

---

**DO THIS NOW!** The fix is simple - just clear cache and redeploy.

