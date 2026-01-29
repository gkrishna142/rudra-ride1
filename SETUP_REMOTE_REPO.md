# How to Set Up Remote Repository and Pull/Push

## Current Situation

✅ **Your code is committed locally** - "nothing to commit, working tree clean" means all files are saved!

❌ **No remote repository configured** - You need to connect to GitHub/GitLab first

---

## Step-by-Step: Set Up Remote Repository

### Step 1: Create Repository on GitHub

1. Go to **https://github.com**
2. Click the **"+"** icon → **"New repository"**
3. Repository name: `admin-backend` (or any name you like)
4. Description: "Django Admin Backend with JWT Authentication"
5. Choose: **Public** or **Private**
6. **DO NOT** check "Initialize with README" (you already have code)
7. Click **"Create repository"**

### Step 2: Copy Repository URL

After creating, GitHub will show you a URL like:
```
https://github.com/yourusername/admin-backend.git
```

**Copy this URL!**

---

## Step 3: Connect Your Local Repository to Remote

### Option A: If you just created the repository (empty)

```bash
# Navigate to your project
cd C:\Users\DELL\Desktop\Admin

# Add remote (replace with your actual GitHub URL)
git remote add origin https://github.com/yourusername/admin-backend.git

# Verify it was added
git remote -v

# Push your code
git push -u origin master
```

### Option B: If repository already has files

```bash
# Add remote
git remote add origin https://github.com/yourusername/admin-backend.git

# Pull first (to get any existing files)
git pull origin master --allow-unrelated-histories

# Then push
git push -u origin master
```

---

## Step 4: Pull from Remote (After Setup)

Once remote is configured, you can pull:

```bash
# Simple pull (if tracking is set up)
git pull

# Or specify remote and branch
git pull origin master
```

---

## Common Commands

### Check Remote
```bash
git remote -v
```

### Remove Remote (if wrong URL)
```bash
git remote remove origin
```

### Change Remote URL
```bash
git remote set-url origin https://github.com/yourusername/new-repo.git
```

### Push to Remote
```bash
git push origin master
# or after first time:
git push
```

### Pull from Remote
```bash
git pull origin master
# or if tracking is set:
git pull
```

---

## Authentication

When you push, GitHub will ask for:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)

### Create Personal Access Token:
1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token
4. Select scopes: `repo` (full control)
5. Copy the token (you'll only see it once!)

---

## Quick Setup Example

```bash
# 1. Add remote
git remote add origin https://github.com/gurypavithra41/admin-backend.git

# 2. Verify
git remote -v

# 3. Push (first time)
git push -u origin master

# 4. Future pulls
git pull

# 5. Future pushes
git push
```

---

## Troubleshooting

### "remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add new one
git remote add origin https://github.com/yourusername/repo.git
```

### "Authentication failed"
- Use Personal Access Token instead of password
- Make sure token has `repo` scope

### "Updates were rejected"
```bash
# Pull first, then push
git pull origin master --allow-unrelated-histories
git push origin master
```

