# ORYN Desktop Companion

Lightweight folder sync tool for ORYN - automatically syncs your local folders to ORYN cloud.

## What is this?

A tiny system tray application (~5-10MB) that:
- Watches your local folders for changes
- Automatically uploads files to ORYN cloud (S3)
- Runs silently in the background
- No UI needed - everything managed through ORYN web app

## Distribution Methods

### Option 1: GitHub Releases (Recommended - What you're already doing)

**Pros:**
✅ Same as your Electron app - you're familiar with this
✅ Free hosting
✅ Automatic updates possible
✅ Users trust GitHub
✅ Simple download links

**How it works:**
1. Build executables for Windows/Mac/Linux
2. Create a GitHub Release (tag: v1.0.0)
3. Upload the executables as release assets
4. Users download from: `https://github.com/yourusername/oryn-companion/releases/latest`

**Setup:**
```bash
# Create new repo
git init
git remote add origin https://github.com/yourusername/oryn-companion.git

# Build executables
python build.py

# Create release (manually on GitHub or use gh CLI)
gh release create v1.0.0 dist/ORYN-Companion.exe dist/ORYN-Companion.app dist/ORYN-Companion
```

### Option 2: Direct Download from Your Server (Simpler)

**Pros:**
✅ Even simpler - no GitHub needed
✅ Full control
✅ Can track downloads

**How it works:**
1. Build executables
2. Upload to your AWS S3 bucket: `oryn-downloads/companion/`
3. Serve via CloudFront or direct S3 URL
4. Users download from: `https://downloads.oryn.com/companion/ORYN-Companion.exe`

**Setup:**
```bash
# Upload to S3
aws s3 cp dist/ORYN-Companion.exe s3://oryn-downloads/companion/ORYN-Companion-v1.0.0.exe --acl public-read
aws s3 cp dist/ORYN-Companion.app s3://oryn-downloads/companion/ORYN-Companion-v1.0.0.app --acl public-read
```

### Option 3: Auto-update via Web App (Most Professional)

**How it works:**
1. User clicks "Download Companion" in web app
2. Web app generates signed download URL from S3
3. User downloads and installs
4. Companion checks for updates on startup
5. Auto-downloads new version if available

**Implementation:**
```python
# Backend endpoint
@app.get("/api/companion/download/{platform}")
async def download_companion(platform: str):
    # Generate signed S3 URL
    s3_key = f"companion/ORYN-Companion-{platform}-latest.exe"
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'oryn-downloads', 'Key': s3_key},
        ExpiresIn=3600
    )
    return {"download_url": url, "version": "1.0.0"}
```

## Building Executables

### Windows
```bash
cd ORYN_DESKTOP_COMPANION
pip install -r requirements.txt
python build.py
# Output: dist/ORYN-Companion.exe (~8MB)
```

### macOS
```bash
cd ORYN_DESKTOP_COMPANION
pip install -r requirements.txt
python build.py
# Output: dist/ORYN-Companion.app
```

### Linux
```bash
cd ORYN_DESKTOP_COMPANION
pip install -r requirements.txt
python build.py
# Output: dist/ORYN-Companion
```

## User Installation

1. Download from GitHub releases or your website
2. Run the executable
3. App minimizes to system tray
4. Open ORYN web app → Settings → Sync
5. Click "Connect Desktop Companion"
6. Follow setup wizard

## My Recommendation for You

Since you're already using GitHub releases for the Electron app:

**Use GitHub Releases for Companion too**
- Create repo: `oryn-companion`
- Build executables weekly or when you update
- Upload as releases
- Frontend button: "Download Companion" → Links to latest GitHub release

**Advantages:**
- Consistent with your current workflow
- No new infrastructure needed
- Free bandwidth
- Users can see release notes
- Familiar process for you

**Simple workflow:**
```bash
# When you want to release
cd ORYN_DESKTOP_COMPANION
python build.py
git tag v1.0.1
git push --tags
# Upload dist files to GitHub release manually or via gh CLI
```

## Size Comparison

- Full Electron app: ~100-200MB
- This Companion: ~5-10MB (90% smaller!)
- Just watches folders + uploads to S3
- No UI, no browser engine

## What's Next?

1. ✅ Create the companion app (Done - this file!)
2. Add backend S3 event handler (I'll do next)
3. Update frontend to show "Download Companion" button
4. Set up GitHub releases (you do this - same as Electron)

Ready to continue?

