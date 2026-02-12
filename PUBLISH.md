# 🚀 Publishing ScholarPulse to GitHub

Follow these steps to securely publish your professional research agent to GitHub.

### 🛠️ Prerequisites: Install Git
It looks like Git is not yet installed on your system.
1. **Download Git**: Go to [git-scm.com/download/win](https://git-scm.com/download/win) and download the 64-bit installer.
2. **Installation**: Run the installer and keep the **default settings** (just click Next).
3. **Restart Terminal**: Close and reopen your terminal/VS Code for the change to take effect.

*Alternative: If you prefer a visual interface, download [GitHub Desktop](https://desktop.github.com/—it's much easier for beginners!)*

---

### ⚠️ Security First
**NEVER** share your `.env` file or API keys. Your `.gitignore` is already configured to hide these from GitHub.

---

### Phase 1: Create a Personal Access Token (Classic)
GitHub now requires a **Token** instead of a password for command-line access.
1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens > Tokens (classic)](https://github.com/settings/tokens).
2. Click **Generate new token (classic)**.
3. Give it a name (e.g., "ScholarPulse-Upload") and check the **repo** box.
4. **Copy the token immediately**—you won't see it again!

---git : The term 'git' is not recognized as the name of a cmdlet, function, script file, or 
operable program. Check the spelling of the name, or if a path was included, verify that the     
path is correct and try again.
At line:1 char:1
+ git push -u origin main
+ ~~~
    + CategoryInfo          : ObjectNotFound: (git:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundExceptiongit : The term 'git' is not recognized as the name of a cmdlet, function, script file, or 
operable program. Check the spelling of the name, or if a path was included, verify that the     
path is correct and try again.
At line:1 char:1
+ git push -u origin main
+ ~~~
    + CategoryInfo          : ObjectNotFound: (git:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

### Phase 2: Initialize & Push
Open your terminal in `e:\AI_Research_Agent` and run these commands one by one:

```powershell
# 1. Initialize Git
git init

# 2. Add all files (respecting .gitignore)
git add .

# 3. Create your first commit
git commit -m "Initial Release: ScholarPulse Noir Edition 🌌"

# 4. Create a main branch
git branch -M main

# 5. Add your remote repository (Replace YOUR_USERNAME and YOUR_REPO)
# git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 6. Push to GitHub
# When it asks for your password, PASTE your Personal Access Token instead.
git push -u origin main
```

---

### Phase 3: Final Touches
Once pushed, visit your GitHub repository page. It will automatically render your **Professional README.md** as the landing page, showing off the "Neon Noir" features to the world!

---

**Success, Researcher! Your project is ready for the global stage.** 🌌💎✨🧬
