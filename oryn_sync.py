#!/usr/bin/env python3
"""
ORYN Desktop Companion - Lightweight Folder Sync
Watches local directories and syncs to ORYN cloud (S3)
"""

import os
import sys
import time
import json
import boto3
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import threading
import pystray
from PIL import Image, ImageDraw
from botocore.exceptions import ClientError
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / '.oryn' / 'sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ORYNConfig:
    """Manages ORYN sync configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.oryn'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        return {
            'user_token': None,
            'user_email': None,
            'watch_folders': [],
            'aws_access_key': None,
            'aws_secret_key': None,
            'aws_region': 'eu-north-1',
            's3_bucket': 'oryn-user-files',
            'backend_url': 'http://localhost:8080'
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def is_configured(self):
        """Check if app is configured"""
        return (self.config.get('user_token') and 
                self.config.get('aws_access_key') and 
                len(self.config.get('watch_folders', [])) > 0)


class ORYNFileHandler(FileSystemEventHandler):
    """Handles file system events and uploads to S3"""
    
    def __init__(self, s3_client, bucket_name, user_email, backend_url):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.user_email = user_email
        self.backend_url = backend_url
        self.upload_queue = []
        self.processing = False
        
    def on_created(self, event):
        """Handle file creation"""
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")
            self.queue_upload(event.src_path, 'created')
    
    def on_modified(self, event):
        """Handle file modification"""
        if not event.is_directory:
            logger.info(f"File modified: {event.src_path}")
            self.queue_upload(event.src_path, 'modified')
    
    def on_deleted(self, event):
        """Handle file deletion"""
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")
            self.handle_deletion(event.src_path)
    
    def queue_upload(self, file_path, event_type):
        """Queue file for upload"""
        self.upload_queue.append({
            'path': file_path,
            'type': event_type,
            'timestamp': datetime.now().isoformat()
        })
        
        if not self.processing:
            threading.Thread(target=self.process_queue, daemon=True).start()
    
    def process_queue(self):
        """Process upload queue"""
        self.processing = True
        while self.upload_queue:
            item = self.upload_queue.pop(0)
            try:
                # Wait a bit to ensure file is fully written
                time.sleep(2)
                if os.path.exists(item['path']):
                    self.upload_to_s3(item['path'])
            except Exception as e:
                logger.error(f"Failed to process {item['path']}: {e}")
        self.processing = False
    
    def upload_to_s3(self, file_path):
        """Upload file to S3"""
        try:
            # Generate S3 key
            file_name = os.path.basename(file_path)
            s3_key = f"{self.user_email}/{file_name}"
            
            # Upload to S3
            logger.info(f"Uploading {file_name} to S3...")
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'Metadata': {
                        'user_email': self.user_email,
                        'original_path': file_path,
                        'upload_time': datetime.now().isoformat()
                    }
                }
            )
            logger.info(f"✅ Uploaded {file_name} successfully")
            
            # Notify backend
            self.notify_backend(s3_key, 'upload')
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
        except Exception as e:
            logger.error(f"Upload error: {e}")
    
    def handle_deletion(self, file_path):
        """Handle file deletion"""
        try:
            file_name = os.path.basename(file_path)
            s3_key = f"{self.user_email}/{file_name}"
            
            # Delete from S3
            logger.info(f"Deleting {file_name} from S3...")
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"✅ Deleted {file_name} from S3")
            
            # Notify backend
            self.notify_backend(s3_key, 'delete')
            
        except Exception as e:
            logger.error(f"Deletion error: {e}")
    
    def notify_backend(self, s3_key, action):
        """Notify ORYN backend of file change"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/file-sync-event",
                json={
                    'user_email': self.user_email,
                    's3_key': s3_key,
                    'action': action,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Backend notified of {action}")
        except Exception as e:
            logger.warning(f"Failed to notify backend: {e}")


class ORYNCompanion:
    """Main ORYN Desktop Companion application"""
    
    def __init__(self):
        self.config = ORYNConfig()
        self.s3_client = None
        self.observer = None
        self.icon = None
        self.running = False
        
    def setup_s3(self):
        """Setup S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.config['aws_access_key'],
                aws_secret_access_key=self.config.config['aws_secret_key'],
                region_name=self.config.config['aws_region']
            )
            logger.info("S3 client configured")
            return True
        except Exception as e:
            logger.error(f"S3 setup failed: {e}")
            return False
    
    def start_watching(self):
        """Start watching configured folders"""
        if not self.config.is_configured():
            logger.error("App not configured. Please run setup first.")
            return False
        
        if not self.setup_s3():
            return False
        
        # Create file handler
        handler = ORYNFileHandler(
            self.s3_client,
            self.config.config['s3_bucket'],
            self.config.config['user_email'],
            self.config.config['backend_url']
        )
        
        # Setup observer
        self.observer = Observer()
        for folder in self.config.config['watch_folders']:
            if os.path.exists(folder):
                self.observer.schedule(handler, folder, recursive=True)
                logger.info(f"Watching: {folder}")
            else:
                logger.warning(f"Folder not found: {folder}")
        
        # Start observer
        self.observer.start()
        self.running = True
        logger.info("🚀 ORYN Desktop Companion started")
        return True
    
    def stop_watching(self):
        """Stop watching folders"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.running = False
            logger.info("ORYN Desktop Companion stopped")
    
    def create_icon(self):
        """Create system tray icon"""
        # Create a simple icon image
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (52, 152, 219))  # ORYN blue
        dc = ImageDraw.Draw(image)
        dc.text((10, 20), "O", fill=(255, 255, 255))
        
        return image
    
    def on_quit(self, icon, item):
        """Handle quit action"""
        logger.info("Quitting ORYN Companion...")
        self.stop_watching()
        icon.stop()
        sys.exit(0)
    
    def on_open_settings(self, icon, item):
        """Open settings"""
        # TODO: Open settings window
        logger.info("Settings clicked")
    
    def get_status_text(self):
        """Get status text for menu"""
        if self.running:
            folders = len(self.config.config.get('watch_folders', []))
            return f"Syncing {folders} folder{'s' if folders != 1 else ''}"
        return "Not running"
    
    def run_in_tray(self):
        """Run application in system tray"""
        icon_image = self.create_icon()
        
        menu = pystray.Menu(
            pystray.MenuItem(self.get_status_text, None, enabled=False),
            pystray.MenuItem('Settings', self.on_open_settings),
            pystray.MenuItem('Quit', self.on_quit)
        )
        
        self.icon = pystray.Icon('ORYN', icon_image, 'ORYN Companion', menu)
        
        # Start watching in background
        if self.start_watching():
            self.icon.run()
        else:
            logger.error("Failed to start watching. Please check configuration.")


def main():
    """Main entry point"""
    print("🚀 ORYN Desktop Companion")
    print("=" * 50)
    
    companion = ORYNCompanion()
    
    # Check if configured
    if not companion.config.is_configured():
        print("\n⚠️  First time setup required")
        print("Please visit: http://localhost:3000/settings/sync")
        print("to configure ORYN Desktop Companion")
        time.sleep(3)
        return
    
    # Run in system tray
    try:
        companion.run_in_tray()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        companion.stop_watching()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

