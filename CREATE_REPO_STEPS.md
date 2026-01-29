# Steps to Create GitHub Repository and Push Code

## Step 1: Create Repository on GitHub

1. **Go to GitHub**: https://github.com
2. **Click the "+" icon** (top right) → **"New repository"**
3. **Repository name**: `Rudra_admin` (exactly as you want it)
4. **Description** (optional): "Django Admin Backend with JWT Authentication"
5. **Choose visibility**:
   - ✅ **Public** (anyone can see)
   - 🔒 **Private** (only you can see)
6. **IMPORTANT**: 
   - ❌ **DO NOT** check "Add a README file"
   - ❌ **DO NOT** check "Add .gitignore"
   - ❌ **DO NOT** check "Choose a license"
   (You already have these files!)
7. **Click "Create repository"**

## Step 2: After Creating Repository

GitHub will show you a page with instructions. **Copy the repository URL** - it should be:
```
https://github.com/gurypavithra41/Rudra_admin.git
```

## Step 3: Push Your Code

After creating the repository, run these commands:

```bash
# Make sure you're in the Admin folder
cd C:\Users\DELL\Desktop\Admin

# Check if remote is already added (we already added it)
git remote -v

# If remote URL is wrong, remove and re-add:
# git remote remove origin
# git remote add origin https://github.com/gurypavithra41/Rudra_admin.git

# Push your code
git push -u origin master
```

## Step 4: Authentication

When you push, GitHub will ask for:
- **Username**: `gurypavithra41`
- **Password**: Use a **Personal Access Token** (NOT your GitHub password)

### Create Personal Access Token:
1. GitHub → Your Profile (top right) → **Settings**
2. Scroll down → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token (classic)**
5. **Note**: "Rudra_admin push"
6. **Expiration**: Choose duration (90 days, 1 year, etc.)
7. **Select scopes**: Check ✅ **repo** (full control of private repositories)
8. **Generate token**
9. **COPY THE TOKEN** (you'll only see it once!)
10. Use this token as your password when pushing

## Alternative: Use GitHub CLI (if installed)

```bash
gh repo create Rudra_admin --public --source=. --remote=origin --push
```

## Troubleshooting

### "Repository not found"
- Make sure repository exists on GitHub
- Check repository name is exactly: `Rudra_admin`
- Check your GitHub username is correct

### "Authentication failed"
- Use Personal Access Token, not password
- Make sure token has `repo` scope

### "Permission denied"
- Check you have access to the repository
- Verify token has correct permissions

