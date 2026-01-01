# Queue-Based System - Quick Start Guide

## Overview

The system now uses a **queue-based architecture** where:
- **Flask API** accepts requests and enqueues jobs (stateless)
- **Worker Process** processes the queue and sends messages (independent, long-running)

## Running the System

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start Flask API (Terminal 1)

```bash
python app.py
```

You should see:
```
============================================================
WhatsApp Bulk Sender - Flask API Server
============================================================

Server will be available at:
  - http://localhost:8080
  ...
```

### Step 3: Start Worker (Terminal 2)

**Important**: Worker must be running to send messages!

```bash
python run_worker.py
```

You should see:
```
Starting WhatsApp Bulk Sender Worker...
Press Ctrl+C to stop the worker
------------------------------------------------------------
```

The worker will:
1. Open Chrome browser
2. Navigate to WhatsApp Web
3. Wait for you to scan QR code
4. Start processing messages from the queue

### Step 4: Create a Job

**Option A: Web Interface**
1. Open http://localhost:8080/app
2. Upload contacts CSV
3. Enter message
4. Click "Start Sending"

**Option B: API**

```bash
curl -X POST http://localhost:8080/send \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: YOUR_SECRET_KEY" \
  -d '{
    "numbers": ["+1234567890", "+9876543210"],
    "message": "Hello from queue system!",
    "delay_min": 4,
    "delay_max": 8
  }'
```

Response:
```json
{
  "success": true,
  "message": "Job created and queued successfully",
  "job_id": 1,
  "total_numbers": 2,
  "note": "Worker process will handle sending. Start worker with: python run_worker.py"
}
```

## Managing Jobs

### Check Job Status

```bash
curl http://localhost:8080/status/1
```

### Pause a Job

```bash
curl -X POST http://localhost:8080/pause/1 \
  -H "X-API-KEY: YOUR_SECRET_KEY"
```

### Resume a Job

```bash
curl -X POST http://localhost:8080/resume/1 \
  -H "X-API-KEY: YOUR_SECRET_KEY"
```

### Stop a Job

```bash
curl -X POST http://localhost:8080/stop/1 \
  -H "X-API-KEY: YOUR_SECRET_KEY"
```

### List All Jobs

```bash
curl http://localhost:8080/jobs
```

## Key Differences from Old System

| Old System | New System |
|------------|------------|
| Flask sends messages directly | Flask enqueues, Worker sends |
| In-memory state (lost on restart) | SQLite persistence (survives restart) |
| Fixed delays | Randomized delays (4-8s base, 20-40s every 10 messages) |
| No retry logic | 3 retry attempts per message |
| Session crashes break everything | Auto-pause on logout, resume after login |
| Single thread in Flask | Independent worker process |
| No pause/resume | Full job control (pause/resume/stop) |

## Worker Behavior

### Automatic Session Management
- If WhatsApp logs out → Worker pauses jobs → Waits for login → Auto-resumes
- If browser crashes → Worker restarts session → Continues processing

### Retry Logic
- Failed messages retry up to 3 times
- After 3 failures → Message marked as permanently failed
- Job continues with remaining messages

### Delays
- Base delay: 4-8 seconds (randomized)
- Every 10 messages: Additional 20-40 second pause
- Simulates human behavior

## Database

All state is stored in `whatsapp_queue.db` (SQLite):
- Jobs table: Campaign information
- Message queue table: Individual messages with status

**Important**: 
- Database persists between restarts
- Worker can be restarted without losing progress
- Flask can be restarted independently

## Troubleshooting

### Worker Not Sending Messages
- Ensure worker is running: `python run_worker.py`
- Check if logged in to WhatsApp Web
- Verify job status: `curl http://localhost:8080/status/<job_id>`

### Session Lost
- Worker will auto-pause jobs
- Scan QR code in Chrome window
- Worker will auto-resume after login

### Messages Stuck
- Check job status for errors
- Restart worker if needed (progress is saved)
- Failed messages will retry automatically

### Flask Restart
- Flask can be restarted anytime
- Worker continues processing independently
- No data loss

## Production Notes

1. **Run worker as service**: Use systemd, supervisor, or PM2
2. **Monitor logs**: Check worker logs for errors
3. **Database backups**: Backup `whatsapp_queue.db` regularly
4. **API key**: Change `API_KEY` in `config.py` for production
5. **Rate limits**: Adjust delays in `config.py` if needed

## Example Workflow

1. Start Flask: `python app.py`
2. Start Worker: `python run_worker.py`
3. Create job via API/web interface
4. Worker processes queue automatically
5. Check status: `GET /status/<job_id>`
6. Pause if needed: `POST /pause/<job_id>`
7. Resume: `POST /resume/<job_id>`
8. Monitor progress via status endpoint
