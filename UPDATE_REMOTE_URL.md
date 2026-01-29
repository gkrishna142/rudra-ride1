# How to Update Remote Repository URL

## If Repository Name is Different

### Step 1: Find Exact Repository Name
1. Go to: https://github.com/gurypavithra41?tab=repositories
2. Find your repository
3. Check the **exact name** (case-sensitive!)

### Step 2: Update Remote URL

```bash
cd C:\Users\DELL\Desktop\Admin

# Remove current remote
git remote remove origin

# Add correct remote (replace with actual name)
git remote add origin https://github.com/gurypavithra41/ACTUAL_REPO_NAME.git

# Verify
git remote -v

# Push
git push -u origin master
```

## Common Variations:
- `Rudra_admin` (current)
- `Rudra-admin` (with dash)
- `rudra_admin` (lowercase)
- `RudraAdmin` (no underscore)
- `rudra-admin` (lowercase with dash)

## Quick Update Command:

```bash
# If repository name is different, update it:
git remote set-url origin https://github.com/gurypavithra41/CORRECT_NAME.git
```

