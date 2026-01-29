# Git Push and Pull Guide

## Prerequisites

### 1. Create a Remote Repository (if you don't have one)

**Option A: GitHub**
1. Go to https://github.com
2. Click "New repository"
3. Name it (e.g., "admin-backend")
4. Don't initialize with README (you already have code)
5. Click "Create repository"
6. Copy the repository URL (e.g., `https://github.com/yourusername/admin-backend.git`)

**Option B: GitLab / Bitbucket**
- Similar process on GitLab.com or Bitbucket.org

---

## Step-by-Step: Push Your Code

### Step 1: Add Remote Repository

```bash
# Navigate to your project
cd C:\Users\DELL\Desktop\Admin

# Add remote repository (replace with your actual repository URL)
git remote add origin https://github.com/yourusername/admin-backend.git

# Verify remote was added
git remote -v
```

### Step 2: Stage Your Files

```bash
# Add all files
git add .

# Or add specific files
git add backend/
git add .gitignore
```

### Step 3: Commit Your Changes

```bash
# Create your first commit
git commit -m "Initial commit: Django admin project with JWT authentication"

# For future commits, use descriptive messages
git commit -m "Add admin login with JWT tokens"
git commit -m "Update admin profile model with name, email, password fields"
```

### Step 4: Push to Remote Repository

```bash
# Push to main/master branch (first time)
git push -u origin master

# Or if your default branch is 'main'
git push -u origin main

# For future pushes (after first time)
git push
```

---

## Step-by-Step: Pull from Repository

### Pull Latest Changes

```bash
# Navigate to your project
cd C:\Users\DELL\Desktop\Admin

# Pull latest changes from remote
git pull origin master

# Or if branch is 'main'
git pull origin main

# Or simply (if already set up)
git pull
```

---

## Common Git Workflow

### Daily Workflow

```bash
# 1. Check status
git status

# 2. Pull latest changes (if working with team)
git pull

# 3. Make your changes (edit files)

# 4. Stage your changes
git add .

# 5. Commit your changes
git commit -m "Description of your changes"

# 6. Push your changes
git push
```

---

## Useful Git Commands

### Check Status
```bash
git status
```

### View Changes
```bash
# See what files changed
git diff

# See staged changes
git diff --staged
```

### View Commit History
```bash
git log
git log --oneline  # Compact view
```

### Create New Branch
```bash
git checkout -b feature-name
git push -u origin feature-name
```

### Switch Branch
```bash
git checkout master
# or
git checkout main
```

### Merge Branch
```bash
git checkout master
git merge feature-name
```

---

## Troubleshooting

### If push is rejected:
```bash
# Pull first, then push
git pull origin master
git push origin master
```

### If you need to force push (use carefully!):
```bash
git push --force origin master
```

### Remove remote (if you added wrong URL):
```bash
git remote remove origin
git remote add origin <correct-url>
```

### Check remote URL:
```bash
git remote -v
```

---

## Example: Complete First Push

```bash
# 1. Navigate to project
cd C:\Users\DELL\Desktop\Admin

# 2. Check status
git status

# 3. Add remote (replace with your GitHub URL)
git remote add origin https://github.com/yourusername/admin-backend.git

# 4. Add all files
git add .

# 5. Commit
git commit -m "Initial commit: Django admin project"

# 6. Push
git push -u origin master
```

---

## Authentication

### For GitHub:
- Use Personal Access Token (not password)
- Generate token: GitHub → Settings → Developer settings → Personal access tokens
- Use token as password when prompted

### For GitLab/Bitbucket:
- Use your account password or access token

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `git add .` | Stage all changes |
| `git commit -m "message"` | Commit with message |
| `git push` | Push to remote |
| `git pull` | Pull from remote |
| `git status` | Check status |
| `git log` | View history |
| `git remote -v` | View remote URLs |

