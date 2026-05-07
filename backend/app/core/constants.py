import os
from pathlib import Path

# Storage configuration
# Railway provides /data as a persistent storage directory
STORAGE_DIR = os.getenv('STORAGE_DIR', '/data')
# STORAGE_DIR = os.getenv('STORAGE_DIR', './data')
AVATARS_DIR = os.path.join(STORAGE_DIR, 'avatars')

# Ensure storage directories exist
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(AVATARS_DIR, exist_ok=True)

# Set proper permissions
os.chmod(STORAGE_DIR, 0o755)
os.chmod(AVATARS_DIR, 0o755)

# Avatar configuration
AVATAR_MAX_SIZE = 5 * 1024 * 1024  # 5MB
AVATAR_SIZE = (256, 256)
ALLOWED_AVATAR_TYPES = ["image/jpeg", "image/png"] 