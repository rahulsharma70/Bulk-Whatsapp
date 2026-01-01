# Starting the Development Server

## Quick Start

### Option 1: Using Python directly (Mac/Linux)
```bash
python3 app.py
```

### Option 2: Using the batch file (Windows)
Double-click `run.bat` or `start_app.bat`

### Option 3: Command line (Windows)
```bash
python app.py
```

## Server URLs

Once the server starts, you'll see:
```
Running on http://0.0.0.0:5000
```

Access the application at:
- **Main Interface:** http://localhost:5000/app
- **Health Check:** http://localhost:5000/
- **Test Route:** http://localhost:5000/test

## Important Notes

1. **API Key:** Make sure to set your API key in:
   - `app.py` (line 26): `app.config['API_KEY'] = 'YOUR_SECRET_KEY'`
   - `templates/index.html` (line 496): `'X-API-KEY': 'YOUR_SECRET_KEY'`

2. **Port 5000:** If port 5000 is already in use:
   - Close other applications using port 5000
   - Or change the port in `app.py` (last line):
     ```python
     app.run(host='0.0.0.0', port=8080, debug=False)
     ```

3. **CORS:** The server has CORS enabled, so it accepts requests from any origin.

## Testing the Server

### Health Check
```bash
curl http://localhost:5000/
```

Expected response:
```json
{"status": "OK", "message": "Server is running"}
```

### Test Route
```bash
curl http://localhost:5000/test
```

### Send Message (with API key)
```bash
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: YOUR_SECRET_KEY" \
  -d '{
    "numbers": ["+919876543210"],
    "message": "Test message",
    "attachments": []
  }'
```

## Troubleshooting

### Server won't start
- Check if Python is installed: `python3 --version`
- Install dependencies: `pip install -r requirements.txt`
- Check for port conflicts: `lsof -i :5000` (Mac/Linux) or `netstat -ano | findstr :5000` (Windows)

### 403 Unauthorized Error
- Make sure the API key in the request header matches the one in `app.py`
- Check that you're sending the `X-API-KEY` header

### Frontend not loading
- Make sure you're accessing http://localhost:5000/app (not just /)
- Check browser console for errors (F12)
- Try a different browser or incognito mode

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

