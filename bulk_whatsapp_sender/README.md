# Bulk WhatsApp Sender

A professional web-based application for sending bulk WhatsApp messages with support for attachments, duplicate filtering, and customizable delays.

## Features

- ✅ **Multiple File Format Support**: Upload contacts via CSV, Excel, or TXT files
- ✅ **No Country Code Limitation**: Works with any country code (not limited to +91)
- ✅ **Duplicate Number Filtering**: Automatically removes duplicate phone numbers
- ✅ **Bulk Messaging**: Send messages to multiple contacts efficiently
- ✅ **Attachment Support**: Send images (JPG, PNG), PDFs, Word documents, and text files
- ✅ **Configurable Delay**: Minimum 15 seconds delay between messages (customizable)
- ✅ **Beautiful Professional UI**: Modern, clean interface with light professional colors
- ✅ **Real-time Progress Tracking**: Monitor sending progress in real-time
- ✅ **Easy Installation**: Simple setup process for Windows

## Requirements

- Python 3.8 or higher
- Google Chrome browser
- Windows OS

## Installation

### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```

### Step 2: Install Dependencies

1. Open Command Prompt in the project directory
2. Run the following command:
   ```
   pip install -r requirements.txt
   ```

### Step 3: Run the Application

1. Double-click `run.bat` or run in Command Prompt:
   ```
   python app.py
   ```
2. Open your browser and go to: `http://127.0.0.1:5000`

## Usage

### 1. Upload Contacts

- Click "Choose File" and select your CSV, Excel, or TXT file
- The application will automatically:
  - Parse phone numbers from the file
  - Remove duplicates
  - Normalize phone numbers (handles any country code)
  - Display statistics and preview

### 2. Compose Message

- Enter your message in the text area
- You can send either a message, an attachment, or both

### 3. Add Attachment (Optional)

- Click "Choose Attachment" to upload:
  - Images: JPG, PNG
  - Documents: PDF, Word (DOC, DOCX), TXT

### 4. Configure Settings

- Set delay between messages (minimum 15 seconds)
- This helps avoid rate limiting

### 5. Send Messages

- Click "Start Sending"
- A Chrome window will open with WhatsApp Web
- Scan the QR code with your phone
- The application will start sending messages automatically
- Monitor progress in real-time

## File Format Examples

### CSV Format
```csv
Phone Number
+1234567890
+919876543210
+441234567890
```

### Excel Format
- First column should contain phone numbers
- Column name can be: Phone, Mobile, Number, Contact, or WhatsApp
- If no matching column found, first column is used

### TXT Format
```
+1234567890
+919876543210
+441234567890
```

## Phone Number Format

- Supports any country code (not limited to +91)
- Can include or exclude + sign
- Spaces, dashes, and other characters are automatically removed
- Examples:
  - `+91 98765 43210`
  - `919876543210`
  - `09876543210`
  - `+1-234-567-8900`

## Important Notes

1. **WhatsApp Web**: You need to scan QR code when Chrome opens
2. **Rate Limiting**: Minimum 15 seconds delay is recommended to avoid account restrictions
3. **Chrome Profile**: The application uses a persistent Chrome profile to maintain login
4. **Internet Connection**: Stable internet connection required
5. **WhatsApp Account**: Use a verified WhatsApp account

## Troubleshooting

### Chrome Driver Issues
- The application automatically downloads ChromeDriver
- If issues occur, ensure Chrome browser is up to date

### QR Code Not Appearing
- Wait a few seconds for WhatsApp Web to load
- Ensure Chrome window is not minimized

### Messages Not Sending
- Verify phone numbers are correct
- Ensure WhatsApp Web is logged in
- Check internet connection
- Some numbers may not be on WhatsApp

### File Upload Errors
- Ensure file format is correct (CSV, XLSX, XLS, or TXT)
- Check file size (max 16MB)
- Verify file is not corrupted

## Security

- All data is processed locally on your computer
- No data is sent to external servers
- Chrome profile is stored locally

## Support

For issues or questions, please check:
- File format is correct
- Phone numbers are valid
- WhatsApp Web is accessible
- Chrome browser is installed and updated

## License

This software is provided as-is for personal and commercial use.

