# Quick Start Guide

## Installation (One-Time Setup)

1. **Install Python** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Run Installation Script**
   - Double-click `install.bat`
   - Wait for installation to complete

## Running the Application

1. **Start the Application**
   - Double-click `run.bat`
   - Or run: `python app.py` in Command Prompt

2. **Open in Browser**
   - Go to: `http://127.0.0.1:5000`
   - The beautiful interface will load

## Sending Your First Bulk Message

### Step 1: Prepare Contacts File

Create a file with phone numbers (CSV, Excel, or TXT):

**Example CSV (sample_contacts.csv):**
```
Phone Number
+919876543210
+1234567890
+441234567890
```

**Example TXT:**
```
+919876543210
+1234567890
+441234567890
```

### Step 2: Upload Contacts

1. Click "Choose File" button
2. Select your contacts file
3. Wait for processing
4. Check the statistics (total, unique, duplicates removed)

### Step 3: Write Message

1. Type your message in the text area
2. Or upload an attachment (optional)
3. Or do both!

### Step 4: Configure Settings

- Set delay between messages (minimum 15 seconds)
- This prevents rate limiting

### Step 5: Send Messages

1. Click "Start Sending" button
2. **Chrome will open automatically**
3. **Scan QR code** with your phone (WhatsApp → Settings → Linked Devices)
4. Messages will start sending automatically
5. Monitor progress in real-time

## Tips

- ✅ **Phone Numbers**: Can be in any format (with/without +, spaces, dashes)
- ✅ **Country Codes**: Works with any country code (not limited to +91)
- ✅ **Duplicates**: Automatically removed
- ✅ **Attachments**: Support JPG, PNG, PDF, Word, TXT
- ✅ **Delay**: Minimum 15 seconds recommended
- ✅ **Progress**: Real-time tracking in the interface

## Troubleshooting

**Chrome doesn't open?**
- Make sure Google Chrome is installed
- Check internet connection

**QR code not appearing?**
- Wait 10-15 seconds
- Refresh Chrome window if needed

**Messages not sending?**
- Verify phone numbers are correct
- Ensure WhatsApp Web is logged in
- Check that numbers are on WhatsApp
- Increase delay time

**Port already in use?**
- Close other applications
- Or change port in `app.py`

## Need Help?

Check `INSTALLATION_GUIDE.md` for detailed troubleshooting.

