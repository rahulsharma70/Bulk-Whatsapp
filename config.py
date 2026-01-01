"""
Configuration file for Bulk WhatsApp Sender
Contains all constants, delays, and settings
"""

import os

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8080
API_KEY = os.getenv('API_KEY', 'YOUR_SECRET_KEY')  # Change this in production
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# File Upload Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'}

# Database Configuration (SQLite)
DB_PATH = 'whatsapp_queue.db'
QUEUE_TABLE = 'message_queue'
JOBS_TABLE = 'jobs'

# Chrome/Selenium Configuration
CHROME_PROFILE_DIR = os.path.abspath("./chrome_profile")
CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Delay Configuration (in seconds)
MIN_DELAY = 4
MAX_DELAY = 8
LONG_PAUSE_INTERVAL = 10  # Every N messages
LONG_PAUSE_MIN = 20
LONG_PAUSE_MAX = 40

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # Seconds to wait before retry

# Session Management
SESSION_CHECK_INTERVAL = 5  # Check session health every N seconds
SESSION_TIMEOUT = 60  # Wait up to 60 seconds for QR scan
LOGIN_CHECK_TIMEOUT = 15  # Wait up to 15 seconds for login verification

# Worker Configuration
WORKER_POLL_INTERVAL = 1  # Check queue every N seconds
WORKER_IDLE_DELAY = 2  # Delay when queue is empty

# WhatsApp Web URLs
WHATSAPP_BASE_URL = "https://web.whatsapp.com"
WHATSAPP_SEND_URL_TEMPLATE = "https://web.whatsapp.com/send?phone={}"

# Job Status Values
JOB_STATUS_PENDING = 'pending'
JOB_STATUS_RUNNING = 'running'
JOB_STATUS_PAUSED = 'paused'
JOB_STATUS_COMPLETED = 'completed'
JOB_STATUS_STOPPED = 'stopped'
JOB_STATUS_WAITING_FOR_LOGIN = 'waiting_for_login'
JOB_STATUS_FAILED = 'failed'

# Message Status Values
MESSAGE_STATUS_PENDING = 'pending'
MESSAGE_STATUS_SENT = 'sent'
MESSAGE_STATUS_FAILED = 'failed'
MESSAGE_STATUS_RETRYING = 'retrying'
