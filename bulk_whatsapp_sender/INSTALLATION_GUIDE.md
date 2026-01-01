# Installation Guide - Bulk WhatsApp Sender

## Quick Start for Windows Users

### Prerequisites

1. **Python 3.8 or Higher**
   - Download from: https://www.python.org/downloads/
   - During installation, **IMPORTANT**: Check the box "Add Python to PATH"
   - Verify installation: Open Command Prompt and type `python --version`

2. **Google Chrome Browser**
   - Download from: https://www.google.com/chrome/
   - The application uses Chrome to access WhatsApp Web

### Installation Steps

#### Method 1: Automatic Installation (Recommended)

1. **Double-click `install.bat`**
   - This will automatically install all required packages
   - Wait for the installation to complete

2. **Double-click `run.bat`** to start the application
   - Or run `python app.py` in Command Prompt

3. **Open your browser** and go to: `http://127.0.0.1:5000`

#### Method 2: Manual Installation

1. **Open Command Prompt** in the project folder
   - Right-click in the folder → "Open in Terminal" or "Open Command Prompt here"

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```
   python app.py
   ```

4. **Open your browser** and go to: `http://127.0.0.1:5000`

## First Time Setup

### 1. Prepare Your Contacts File

Create a CSV, Excel, or TXT file with phone numbers:

**CSV Format (sample_contacts.csv):**
```csv
Phone Number
+919876543210
+1234567890
+441234567890
```

**TXT Format:**
```
+919876543210
+1234567890
+441234567890
```

**Excel Format:**
- First column should contain phone numbers
- Column header can be: Phone, Mobile, Number, Contact, or WhatsApp

### 2. Using the Application

1. **Upload Contacts:**
   - Click "Choose File" and select your contacts file
   - The app will automatically remove duplicates
   - Check the statistics displayed

2. **Compose Message:**
   - Type your message in the text area
   - Or upload an attachment (optional)

3. **Configure Settings:**
   - Set delay between messages (minimum 15 seconds)

4. **Start Sending:**
   - Click "Start Sending"
   - Chrome will open with WhatsApp Web
   - **Scan the QR code** with your phone
   - Messages will start sending automatically

## Troubleshooting

### Python Not Found
- **Problem:** "python is not recognized"
- **Solution:** 
  - Reinstall Python and check "Add Python to PATH"
  - Or use `py` instead of `python` in commands

### Package Installation Fails
- **Problem:** pip install fails
- **Solution:**
  - Update pip: `python -m pip install --upgrade pip`
  - Try: `pip install -r requirements.txt --user`

### Chrome Driver Issues
- **Problem:** ChromeDriver errors
- **Solution:**
  - Update Chrome browser to latest version
  - The app automatically downloads ChromeDriver

### QR Code Not Appearing
- **Problem:** WhatsApp Web doesn't load
- **Solution:**
  - Wait 10-15 seconds for page to load
  - Check internet connection
  - Try refreshing the Chrome window

### Messages Not Sending
- **Problem:** Messages fail to send
- **Solution:**
  - Verify phone numbers are correct and include country code
  - Ensure WhatsApp Web is logged in (QR code scanned)
  - Check that numbers are registered on WhatsApp
  - Increase delay time if rate limited

### Port Already in Use
- **Problem:** "Address already in use"
- **Solution:**
  - Close other applications using port 5000
  - Or change port in `app.py`: `app.run(port=5001)`

## System Requirements

- **OS:** Windows 7/8/10/11
- **RAM:** Minimum 4GB (8GB recommended)
- **Storage:** 500MB free space
- **Internet:** Stable broadband connection
- **Browser:** Google Chrome (latest version)

## Security Notes

- All processing happens locally on your computer
- No data is sent to external servers
- Chrome profile is stored in `chrome_profile/` folder
- Uploaded files are stored in `uploads/` folder
- You can delete these folders to clear data

## Support

For common issues:
1. Check that Python is installed correctly
2. Verify all dependencies are installed
3. Ensure Chrome browser is up to date
4. Check internet connection
5. Verify WhatsApp Web is accessible

## Uninstallation

To remove the application:
1. Delete the project folder
2. Optionally remove Python packages:
   ```
   pip uninstall Flask selenium pandas openpyxl xlrd webdriver-manager Werkzeug
   ```

## Updates

To update the application:
1. Download latest version
2. Run `install.bat` again to update dependencies
3. Restart the application

