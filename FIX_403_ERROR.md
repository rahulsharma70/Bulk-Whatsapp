# Fix 403 Error - Step by Step Guide

## Immediate Solutions (Try These First)

### Solution 1: Use Test Server (Recommended First Step)

1. **Run the test server to verify Flask works:**
   ```bash
   python test_server.py
   ```
   Or double-click `fix_403.bat`

2. **Open browser and go to:**
   - `http://localhost:5000`
   - `http://127.0.0.1:5000`

3. **If test server works:**
   - Flask is working correctly
   - The issue is with the main app configuration
   - Proceed to Solution 2

4. **If test server also gives 403:**
   - It's a browser or system security issue
   - Proceed to Solution 3

### Solution 2: Clear Browser Cache and Try Different Browser

1. **Clear browser cache:**
   - Chrome: `Ctrl+Shift+Delete` → Clear cached images and files
   - Firefox: `Ctrl+Shift+Delete` → Clear cache
   - Edge: `Ctrl+Shift+Delete` → Clear browsing data

2. **Try different browsers:**
   - Chrome
   - Firefox
   - Edge
   - Safari (Mac)

3. **Try incognito/private mode:**
   - Chrome: `Ctrl+Shift+N`
   - Firefox: `Ctrl+Shift+P`
   - Edge: `Ctrl+Shift+N`

### Solution 3: Check if App is Actually Running

1. **Look at the terminal/command prompt:**
   - You should see: `Running on http://0.0.0.0:5000`
   - If you see errors, fix those first

2. **Verify the app started:**
   - Check for any error messages in the terminal
   - Make sure you see "Starting Server" message

3. **If app didn't start:**
   ```bash
   # Install dependencies first
   pip install -r requirements.txt
   
   # Then run
   python app.py
   ```

### Solution 4: Try Different Port

If port 5000 is blocked, change to a different port:

1. **Edit `app.py`** - Find this line (near the end):
   ```python
   app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
   ```

2. **Change port to 8080:**
   ```python
   app.run(debug=True, host='0.0.0.0', port=8080, threaded=True, use_reloader=False)
   ```

3. **Access at:** `http://localhost:8080`

### Solution 5: Check Windows Firewall

1. **Open Windows Security:**
   - Go to Settings → Windows Security → Firewall & network protection

2. **Allow Python through firewall:**
   - Click "Allow an app through firewall"
   - Find Python and check both Private and Public
   - If Python is not listed, click "Allow another app" and add Python

### Solution 6: Disable Antivirus Temporarily

1. **Temporarily disable antivirus** (for testing only)
2. **Try accessing the app**
3. **If it works, add Python to antivirus exceptions**

### Solution 7: Run as Administrator

1. **Right-click Command Prompt**
2. **Select "Run as administrator"**
3. **Navigate to project folder:**
   ```bash
   cd "C:\path\to\your\project"
   ```
4. **Run the app:**
   ```bash
   python app.py
   ```

### Solution 8: Check File Permissions

1. **Right-click the project folder**
2. **Properties → Security**
3. **Make sure your user has Full Control**
4. **Apply to all subfolders and files**

### Solution 9: Use IP Address Instead

Try accessing using your local IP:

1. **Find your IP address:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (usually 192.168.x.x)

2. **Access using:** `http://192.168.x.x:5000`

### Solution 10: Reinstall Flask

If nothing works, reinstall Flask:

```bash
pip uninstall Flask flask-cors
pip install Flask==3.0.0 flask-cors==4.0.0
```

## Quick Diagnostic Commands

Run these to diagnose the issue:

```bash
# Check if Python is working
python --version

# Check if Flask is installed
python -c "import flask; print(flask.__version__)"

# Check if port 5000 is in use
netstat -ano | findstr :5000

# Test Flask with simple server
python test_server.py
```

## Most Common Causes

1. **Browser blocking localhost** - Try different browser or incognito mode
2. **App not actually running** - Check terminal for errors
3. **Port already in use** - Change port number
4. **Firewall blocking** - Allow Python through firewall
5. **Antivirus blocking** - Add Python to exceptions
6. **Cache issues** - Clear browser cache

## Still Not Working?

1. **Check terminal output** - Copy any error messages
2. **Try test_server.py** - This will tell us if Flask works at all
3. **Check browser console** - Press F12 → Console tab for errors
4. **Try curl command:**
   ```bash
   curl http://localhost:5000/test
   ```
   If this works, it's a browser issue

## Success Indicators

You'll know it's working when:
- Terminal shows: "Running on http://0.0.0.0:5000"
- Browser shows the Bulk WhatsApp Sender interface
- No 403 error appears
- `/test` route returns JSON: `{"status": "success"}`

