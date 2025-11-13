#!/usr/bin/env python3
"""
Build script for ORYN Desktop Companion
Creates standalone executables for Windows, Mac, and Linux
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_windows():
    """Build Windows executable"""
    print("🔨 Building Windows executable...")
    
    cmd = [
        'pyinstaller',
        '--name=ORYN-Companion',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',  # You'll need to add this
        '--add-data=icon.ico;.',
        '--hidden-import=watchdog',
        '--hidden-import=boto3',
        '--hidden-import=requests',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        'oryn_sync.py'
    ]
    
    subprocess.run(cmd, check=True)
    print("✅ Windows build complete: dist/ORYN-Companion.exe")

def build_mac():
    """Build macOS app"""
    print("🔨 Building macOS app...")
    
    cmd = [
        'pyinstaller',
        '--name=ORYN-Companion',
        '--onefile',
        '--windowed',
        '--icon=icon.icns',  # You'll need to add this
        '--osx-bundle-identifier=com.oryn.companion',
        '--hidden-import=watchdog',
        '--hidden-import=boto3',
        '--hidden-import=requests',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        'oryn_sync.py'
    ]
    
    subprocess.run(cmd, check=True)
    print("✅ macOS build complete: dist/ORYN-Companion.app")

def build_linux():
    """Build Linux executable"""
    print("🔨 Building Linux executable...")
    
    cmd = [
        'pyinstaller',
        '--name=ORYN-Companion',
        '--onefile',
        '--hidden-import=watchdog',
        '--hidden-import=boto3',
        '--hidden-import=requests',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        'oryn_sync.py'
    ]
    
    subprocess.run(cmd, check=True)
    print("✅ Linux build complete: dist/ORYN-Companion")

def main():
    """Main build function"""
    print("🚀 ORYN Desktop Companion Builder")
    print("=" * 50)
    
    # Detect platform
    if sys.platform == 'win32':
        build_windows()
    elif sys.platform == 'darwin':
        build_mac()
    elif sys.platform.startswith('linux'):
        build_linux()
    else:
        print(f"❌ Unsupported platform: {sys.platform}")
        sys.exit(1)
    
    print("\n✅ Build complete!")
    print(f"📦 Executable location: {Path('dist').absolute()}")

if __name__ == "__main__":
    main()

