# ORYN Desktop Companion - Distribution Guide

## ✅ What's Been Created

1. **Desktop Companion App** (`oryn_sync.py`)
   - Watches local folders
   - Uploads to S3 automatically
   - System tray application
   - ~5-10MB when compiled

2. **Backend Integration** (`s3_event_handler.py` + endpoint in `main.py`)
   - Processes S3 upload events
   - Handles file indexing automatically
   - Works with both manual uploads and companion uploads

3. **Frontend Component** (`DesktopCompanionDownload.jsx`)
   - Beautiful download page in Files section
   - Platform detection (Windows/Mac/Linux)
   - Setup instructions

## 🚀 How Users Will Experience It

### Step 1: User visits Files page
They see a prominent card at the top:
```
┌──────────────────────────────────────────────┐
│  ORYN Desktop Companion                      │
│  Automatically sync your local folders       │
│                                              │
│  ✓ Auto-Sync  ✓ Lightweight  ✓ Secure      │
│                                              │
│  [ Download for Windows ]                    │
└──────────────────────────────────────────────┘
```

### Step 2: Download & Install
- Clicks button → Downloads from GitHub releases
- Runs installer (takes 10 seconds)
- App opens, shows: "Sign in with ORYN"

### Step 3: Setup
- Opens browser to your web app for OAuth
- Returns to app, shows: "Choose folders to sync"
- User selects: `C:\Users\John\Documents\Work`
- App starts syncing → Minimizes to system tray

### Step 4: Daily Use
- User saves `report.pdf` to `Work` folder
- Companion detects it within 5 seconds
- Uploads to S3: `oryn-user-files/john@email.com/report.pdf`
- Backend processes it automatically
- 30 seconds later: searchable in ORYN web app!

## 📦 Distribution Options (You Choose)

### Option A: GitHub Releases (Recommended - You're Already Doing This)

**Setup:**
```bash
# Create new repository
cd ORYN_DESKTOP_COMPANION
git init
git remote add origin https://github.com/yourusername/oryn-companion.git
git add .
git commit -m "Initial ORYN Companion"
git push -u origin main

# Build executables
python build.py

# Create release
git tag v1.0.0
git push --tags

# Upload to GitHub releases (manually or with gh CLI)
gh release create v1.0.0 \
  dist/ORYN-Companion.exe \
  --title "ORYN Companion v1.0.0" \
  --notes "Initial release"
```

**Update `DesktopCompanionDownload.jsx`:**
```javascript
const downloadLinks = {
  windows: 'https://github.com/YOURUSERNAME/oryn-companion/releases/latest/download/ORYN-Companion.exe',
  mac: 'https://github.com/YOURUSERNAME/oryn-companion/releases/latest/download/ORYN-Companion.dmg',
  linux: 'https://github.com/YOURUSERNAME/oryn-companion/releases/latest/download/ORYN-Companion'
}
```

### Option B: S3 Direct Download (Simpler - No GitHub Needed)

**Setup:**
```bash
# Build
python build.py

# Upload to your S3
aws s3 cp dist/ORYN-Companion.exe s3://oryn-downloads/companion/ORYN-Companion-v1.0.0.exe --acl public-read

# Or use your existing S3 bucket
aws s3 cp dist/ORYN-Companion.exe s3://your-bucket/downloads/companion.exe --acl public-read
```

**Update `DesktopCompanionDownload.jsx`:**
```javascript
const downloadLinks = {
  windows: 'https://your-bucket.s3.amazonaws.com/downloads/companion.exe',
  mac: 'https://your-bucket.s3.amazonaws.com/downloads/companion.dmg',
  linux: 'https://your-bucket.s3.amazonaws.com/downloads/companion'
}
```

## 🔧 Building Executables

### Windows:
```bash
cd ORYN_DESKTOP_COMPANION
pip install -r requirements.txt
python build.py
# Output: dist/ORYN-Companion.exe (~8MB)
```

### macOS:
```bash
cd ORYN_DESKTOP_COMPANION
pip install -r requirements.txt
python build.py
# Output: dist/ORYN-Companion.app
```

### Linux:
```bash
cd ORYN_DESKTOP_COMPANION
pip install -r requirements.txt
python build.py
# Output: dist/ORYN-Companion
```

## 📝 What You Need to Do Next

### 1. Update GitHub Links (If using GitHub releases)
In `DesktopCompanionDownload.jsx`, replace:
```javascript
windows: 'https://github.com/yourusername/oryn-companion/releases/latest/download/ORYN-Companion-Windows.exe'
```
With your actual GitHub username.

### 2. Build the Companion App
```bash
cd F:\ORYN + CLERK\ORYN\ORYN_DESKTOP_COMPANION
pip install -r requirements.txt
python build.py
```

### 3. Create GitHub Release (or upload to S3)
- **GitHub**: Create `oryn-companion` repo, build, upload as release
- **S3**: Build and upload to your S3 bucket

### 4. Add AWS Credentials to .env
Users will need to configure these (or you provide them via backend API):
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=eu-north-1
S3_BUCKET_NAME=oryn-user-files
```

## 🎯 Summary

**What users get:**
- 3 ways to add files:
  1. ✅ Manual upload (already works)
  2. ✅ Desktop Companion (NEW - automatic sync)
  3. 🚧 Google Drive integration (future)

**What you need to do:**
1. Build the companion app executables
2. Upload to GitHub releases OR S3
3. Update download links in frontend
4. Done!

**File size comparison:**
- Full Electron app: ~150MB
- Desktop Companion: ~8MB (95% smaller!)
- Just does folder sync, uses web app for everything else

## 🔐 Security Note

The companion app needs AWS credentials to upload to S3. You have two options:

**Option A: User provides their own AWS keys**
- More secure
- User has full control
- Requires more setup

**Option B: You provide temporary credentials via backend**
- Backend generates STS temporary credentials
- User doesn't need AWS account
- Simpler for users
- You manage all S3 access

I recommend **Option B** for better UX. Let me know if you want me to implement the STS credential generation!

