# Troubleshooting Guide

## HTTP 403 Error - Access Denied

If you're getting a **403 Forbidden** error when trying to access `http://127.0.0.1:5000`, try these solutions:

### Solution 1: Check if the App is Running

1. **Verify the app is running:**
   - Check the Command Prompt/Terminal window where you ran `python app.py`
   - You should see: ` * Running on http://127.0.0.1:5000` or `Running on http://0.0.0.0:5000`

2. **If not running:**
   - Make sure you've installed dependencies: `pip install -r requirements.txt`
   - Try running again: `python app.py`

### Solution 2: Try Different URLs

Try these URLs in your browser:
- `http://localhost:5000`
- `http://127.0.0.1:5000`
- `http://0.0.0.0:5000`

### Solution 3: Check Browser Settings

1. **Clear browser cache:**
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Clear cached images and files

2. **Try a different browser:**
   - Chrome
   - Firefox
   - Edge
   - Safari

3. **Disable browser extensions:**
   - Some security extensions block localhost access
   - Try incognito/private mode

### Solution 4: Check Firewall/Antivirus

1. **Windows Firewall:**
   - Go to Windows Security → Firewall & network protection
   - Allow Python through firewall if prompted

2. **Antivirus Software:**
   - Temporarily disable to test
   - Add Python to exceptions if needed

### Solution 5: Check Port Availability

1. **Check if port 5000 is in use:**
   ```bash
   # Windows
   netstat -ano | findstr :5000
   
   # Mac/Linux
   lsof -i :5000
   ```

2. **If port is in use:**
   - Close the application using port 5000
   - Or change port in `app.py`:
     ```python
     app.run(debug=True, host='0.0.0.0', port=5001)
     ```

### Solution 6: Reinstall Dependencies

1. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Reinstall requirements:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### Solution 7: Check Python Installation

1. **Verify Python is installed:**
   ```bash
   python --version
   ```

2. **If using Python 3 specifically:**
   ```bash
   python3 --version
   python3 app.py
   ```

### Solution 8: Run with Admin/Administrator Rights

1. **Windows:**
   - Right-click Command Prompt → "Run as administrator"
   - Navigate to project folder
   - Run `python app.py`

2. **Mac/Linux:**
   - Use `sudo` if needed (not recommended for Flask apps)

### Solution 9: Check File Permissions

1. **Ensure you have read/write permissions:**
   - Check that you can read/write in the project folder
   - Check that `templates/` folder exists and contains `index.html`

### Solution 10: Alternative - Use Different Host

If nothing works, try modifying `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000, threaded=True)
```

Or:

```python
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080, threaded=True)
```

Then access: `http://localhost:8080`

## Common Error Messages

### "ModuleNotFoundError: No module named 'flask'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### "Address already in use"
**Solution:** 
- Close other applications using port 5000
- Or change port number in `app.py`

### "Template not found"
**Solution:**
- Ensure `templates/index.html` exists
- Check file structure is correct

### "ChromeDriver not found"
**Solution:**
- The app automatically downloads ChromeDriver
- Ensure Chrome browser is installed
- Check internet connection

## Still Having Issues?

1. **Check the terminal/command prompt output** for error messages
2. **Try running in verbose mode:**
   ```bash
   python app.py --verbose
   ```
3. **Check Python version:** Should be 3.8 or higher
4. **Verify all files are present:**
   - `app.py`
   - `templates/index.html`
   - `requirements.txt`

## Getting Help

If none of these solutions work:
1. Copy the full error message from the terminal
2. Note which browser you're using
3. Check your operating system version
4. Verify Python version: `python --version`

