# Architecture Documentation

## Overview

The WhatsApp Bulk Sender has been refactored into a **safe, queue-based, resumable architecture** that separates concerns and provides robust error handling.

## Architecture Components

```
┌─────────────────┐
│   Flask API     │  (Stateless - accepts requests only)
│   (app.py)      │
└────────┬────────┘
         │
         │ Enqueues jobs
         ▼
┌─────────────────┐
│  Queue Manager  │  (message_queue/queue_manager.py)
│   Job Store     │  (message_queue/job_store.py) - SQLite
└────────┬────────┘
         │
         │ Persistent storage
         │ (SQLite database)
         ▼
┌─────────────────┐
│  Worker Process │  (worker/worker.py)
│  (run_worker.py)│  (Long-running, independent)
└────────┬────────┘
         │
         │ Sends messages
         ▼
┌─────────────────┐
│  WhatsApp Web   │  (Selenium)
│  Session Manager│  (worker/session_manager.py)
│  Message Sender │  (worker/sender.py)
└─────────────────┘
```

## Key Components

### 1. Flask API (app.py)
- **Stateless**: Never sends messages directly
- **Endpoints**:
  - `POST /send` - Create and enqueue a job
  - `GET /status/<job_id>` - Get job status
  - `POST /pause/<job_id>` - Pause a job
  - `POST /resume/<job_id>` - Resume a job
  - `POST /stop/<job_id>` - Stop a job
  - `GET /jobs` - List all active jobs
  - `POST /upload` - Upload contacts file
  - `POST /upload_attachment` - Upload attachment

### 2. Queue System (message_queue/)
- **queue_manager.py**: High-level interface for queue operations
- **job_store.py**: SQLite-based persistent storage
  - Jobs table: Campaign metadata
  - Message queue table: Individual messages with status

### 3. Worker Process (worker/)
- **worker.py**: Main processing loop
- **session_manager.py**: WhatsApp Web login and session management
- **sender.py**: Message sending with retry logic
- **delay.py**: Randomized human-like delays

### 4. Utilities (utils/)
- **csv_parser.py**: File parsing and phone normalization
- **logger.py**: Structured logging

## Data Flow

1. **Job Creation**:
   - User uploads CSV → Flask parses → Creates job in SQLite → Returns job_id

2. **Message Processing**:
   - Worker polls queue → Gets next pending message → Sends via WhatsApp Web → Updates status

3. **State Management**:
   - All state stored in SQLite
   - Worker can be restarted without data loss
   - Flask restart doesn't affect worker

## Job States

- `pending`: Job created, not started
- `running`: Job is being processed
- `paused`: Job paused by user
- `waiting_for_login`: Session lost, waiting for reconnection
- `completed`: All messages processed
- `stopped`: Job stopped by user
- `failed`: Job failed permanently

## Message States

- `pending`: Not yet sent
- `sent`: Successfully sent
- `failed`: Failed after max retries
- `retrying`: Currently being retried

## Safety Features

1. **Persistent Queue**: SQLite ensures no data loss
2. **Retry Logic**: Up to 3 attempts per message
3. **Session Recovery**: Auto-pause on logout, resume after login
4. **Randomized Delays**: Human-like behavior (4-8s base, 20-40s every 10 messages)
5. **Graceful Shutdown**: Worker handles SIGINT/SIGTERM
6. **Job Control**: Pause, resume, stop at any time

## Running the System

### Step 1: Start Flask API
```bash
python app.py
```

### Step 2: Start Worker (in separate terminal)
```bash
python run_worker.py
```

### Step 3: Use the API
- Web interface: http://localhost:8080/app
- API endpoint: POST http://localhost:8080/send

## Important Notes

1. **Flask and Worker are independent**: Restarting Flask doesn't affect the worker
2. **Worker must be running**: Messages won't be sent without the worker
3. **Database location**: `whatsapp_queue.db` (SQLite file)
4. **Chrome profile**: Persistent profile in `./chrome_profile`
5. **Session management**: Worker handles QR code scanning automatically

## File Structure

```
/bulk_whatsapp_sender
│
├── app.py                     # Flask API (stateless)
├── config.py                  # Configuration
├── run_worker.py              # Worker entry point
├── requirements.txt
│
├── message_queue/
│   ├── __init__.py
│   ├── queue_manager.py       # Queue operations
│   └── job_store.py           # SQLite persistence
│
├── worker/
│   ├── __init__.py
│   ├── worker.py              # Main worker loop
│   ├── session_manager.py     # WhatsApp session
│   ├── sender.py              # Message sender
│   └── delay.py               # Delay generator
│
├── utils/
│   ├── __init__.py
│   ├── csv_parser.py          # File parsing
│   └── logger.py              # Logging
│
├── templates/
│   └── index.html
│
└── uploads/                   # Uploaded files
```

## Configuration

All settings are in `config.py`:
- Delays: `MIN_DELAY`, `MAX_DELAY`, `LONG_PAUSE_*`
- Retry: `MAX_RETRY_ATTEMPTS`
- Database: `DB_PATH`
- Chrome: `CHROME_PROFILE_DIR`, `CHROME_BINARY_PATH`
- Flask: `FLASK_HOST`, `FLASK_PORT`, `API_KEY`
