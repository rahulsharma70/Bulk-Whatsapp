from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from werkzeug.utils import secure_filename
import threading
import json

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows all localhost access from browser

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['API_KEY'] = 'YOUR_SECRET_KEY'  # Change this to your actual API key
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.url_map.strict_slashes = False

def check_api_key():
    """Middleware to check API key for protected endpoints"""
    api_key = request.headers.get("X-API-KEY")
    if api_key != app.config['API_KEY']:
        return jsonify({"error": "Unauthorized"}), 403
    return None

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_phone_number(phone):
    """Normalize phone number - remove spaces, dashes, and handle country codes"""
    # Remove all non-digit characters except +
    phone = re.sub(r'[^\d+]', '', str(phone))
    
    # Remove leading zeros
    phone = phone.lstrip('0')
    
    # If it doesn't start with +, add it (assuming it's a valid number)
    if not phone.startswith('+'):
        # If it starts with country code without +, add +
        if len(phone) >= 10:
            phone = '+' + phone
    
    return phone

def read_contacts_from_file(filepath):
    """Read contacts from CSV, Excel, or TXT file"""
    contacts = []
    
    # Convert to absolute path
    filepath = os.path.abspath(filepath)
    
    # Check if file exists
    if not os.path.exists(filepath):
        # Try to find the file with different name variations
        upload_dir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        
        # List all files in upload directory for debugging
        if os.path.exists(upload_dir):
            available_files = os.listdir(upload_dir)
            raise Exception(
                f"File not found: {filepath}\n"
                f"Looking for: {filename}\n"
                f"Available files in uploads: {', '.join(available_files) if available_files else 'None'}\n"
                f"Please re-upload the file."
            )
        else:
            raise Exception(f"Upload directory not found: {upload_dir}")
    
    # Get file extension
    if '.' not in filepath:
        raise Exception("File has no extension. Please use .csv, .xlsx, .xls, or .txt files.")
    
    file_ext = filepath.rsplit('.', 1)[1].lower()
    
    try:
        if file_ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        contacts.append(normalize_phone_number(line))
        elif file_ext in ['csv', 'xlsx', 'xls']:
            if file_ext == 'csv':
                # Try different encodings for CSV
                try:
                    df = pd.read_csv(filepath, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(filepath, encoding='latin-1')
                    except:
                        df = pd.read_csv(filepath, encoding='iso-8859-1')
            else:
                df = pd.read_excel(filepath)
            
            # Try to find phone number column
            phone_col = None
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['phone', 'mobile', 'number', 'contact', 'whatsapp', 'mob']):
                    phone_col = col
                    break
            
            # If no phone column found, use first column
            if phone_col is None:
                phone_col = df.columns[0]
            
            for phone in df[phone_col].dropna():
                normalized = normalize_phone_number(phone)
                if normalized:
                    contacts.append(normalized)
    except FileNotFoundError:
        raise Exception(f"File not found: {filepath}")
    except pd.errors.EmptyDataError:
        raise Exception("The file is empty. Please check your file and try again.")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")
    
    return contacts

def remove_duplicates(contacts):
    """Remove duplicate phone numbers"""
    seen = set()
    unique_contacts = []
    for contact in contacts:
        if contact not in seen:
            seen.add(contact)
            unique_contacts.append(contact)
    return unique_contacts

# Global variables for sending status
sending_status = {
    'is_sending': False,
    'current_index': 0,
    'total': 0,
    'success_count': 0,
    'failed_count': 0,
    'current_contact': '',
    'error_message': ''
}

# Add request logging middleware
@app.before_request
def log_request_info():
    """Log all incoming requests for debugging"""
    print(f"[REQUEST] {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    """Add headers to allow access"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ---- Health Check ----
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "message": "Server is running"}), 200

@app.route('/index')
@app.route('/index.html')
@app.route('/app')
def index():
    """Serve the web interface"""
    try:
        template_path = os.path.join('templates', 'index.html')
        if not os.path.exists(template_path):
            return jsonify({"error": "Template not found"}), 404
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": f"Error loading template: {str(e)}"}), 500

@app.route('/test')
def test():
    """Test route to verify Flask is working"""
    return jsonify({
        'status': 'success',
        'message': 'Flask is working!',
        'timestamp': time.time()
    })

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access forbidden. Please check your browser settings or try a different browser.'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Use secure_filename to handle spaces and special characters
        original_filename = file.filename
        filename = secure_filename(file.filename)
        
        # If secure_filename removed everything, use a timestamp-based name
        if not filename:
            file_ext = original_filename.rsplit('.', 1)[1] if '.' in original_filename else 'csv'
            filename = f"upload_{int(time.time())}.{file_ext}"
        
        # Ensure uploads directory exists
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create full filepath using absolute path
        filepath = os.path.abspath(os.path.join(upload_dir, filename))
        
        # Save file
        try:
            file.save(filepath)
            
            # Verify file was saved
            if not os.path.exists(filepath):
                return jsonify({
                    'error': f'Failed to save file.',
                    'expected_path': filepath,
                    'upload_dir': os.path.abspath(upload_dir),
                    'filename': filename
                }), 500
            
        except Exception as e:
            return jsonify({
                'error': f'Error saving file: {str(e)}',
                'filename': filename,
                'upload_dir': upload_dir
            }), 500
        
        # Read and process file
        try:
            contacts = read_contacts_from_file(filepath)
            unique_contacts = remove_duplicates(contacts)
            
            return jsonify({
                'success': True,
                'total': len(contacts),
                'unique': len(unique_contacts),
                'duplicates': len(contacts) - len(unique_contacts),
                'contacts': unique_contacts[:100],  # Return first 100 for preview
                'filename': filename,
                'filepath': filepath
            })
        except Exception as e:
            # Clean up file if reading failed
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            return jsonify({'error': str(e)}), 400
    
    return jsonify({'error': 'Invalid file type. Allowed: CSV, Excel, TXT'}), 400

@app.route('/upload_attachment', methods=['POST'])
def upload_attachment():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

def send_whatsapp_message(driver, phone_number, message, attachment_path=None, delay=15):
    """Send WhatsApp message to a phone number"""
    try:
        # Remove + from phone number for URL
        phone_clean = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        
        # Open WhatsApp chat
        url = f"https://web.whatsapp.com/send?phone={phone_clean}"
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Check if number is valid (look for error message or chat input)
        try:
            wait = WebDriverWait(driver, 15)
            
            # Check for invalid number error
            try:
                error_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'Phone number shared via url is invalid')]")
                if error_elements:
                    return False, "Invalid phone number"
            except:
                pass
            
            # Try multiple selectors for message input box
            message_box = None
            selectors = [
                "//div[@contenteditable='true'][@data-tab='10']",
                "//div[@contenteditable='true'][@role='textbox']",
                "//div[@contenteditable='true'][@data-tab='9']",
                "//div[contains(@class, 'selectable-text')]//div[@contenteditable='true']",
                "//footer//div[@contenteditable='true']"
            ]
            
            for selector in selectors:
                try:
                    message_box = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    if message_box:
                        break
                except:
                    continue
            
            if not message_box:
                return False, "Could not find message input box"
            
            # If attachment is provided, send it first
            if attachment_path:
                # Convert to absolute path and verify it exists
                attachment_path = os.path.abspath(attachment_path)
                if not os.path.exists(attachment_path):
                    return False, f"Attachment file not found: {attachment_path}"
                try:
                    # Wait a bit more for page to fully load
                    time.sleep(2)
                    
                    # Find attachment button - try multiple selectors
                    attachment_button = None
                    attach_selectors = [
                        "//span[@data-icon='attach-menu-plus']",
                        "//span[@data-testid='attach-menu-plus']",
                        "//button[@title='Attach']",
                        "//div[@title='Attach']"
                    ]
                    
                    for selector in attach_selectors:
                        try:
                            attachment_button = driver.find_element(By.XPATH, selector)
                            if attachment_button:
                                break
                        except:
                            continue
                    
                    if attachment_button:
                        attachment_button.click()
                        time.sleep(2)
                        
                        # Find file input
                        file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                        if file_inputs:
                            file_inputs[0].send_keys(os.path.abspath(attachment_path))
                            time.sleep(3)
                            
                            # Find and click send button
                            send_selectors = [
                                "//span[@data-icon='send']",
                                "//span[@data-testid='send']",
                                "//button[@aria-label='Send']"
                            ]
                            
                            for selector in send_selectors:
                                try:
                                    send_btn = driver.find_element(By.XPATH, selector)
                                    send_btn.click()
                                    time.sleep(3)
                                    break
                                except:
                                    continue
                except Exception as e:
                    return False, f"Error attaching file: {str(e)}"
            
            # Type and send message
            if message:
                try:
                    message_box.click()
                    time.sleep(1)
                    
                    # Clear any existing text
                    message_box.send_keys(Keys.CONTROL + "a")
                    message_box.send_keys(Keys.DELETE)
                    time.sleep(0.5)
                    
                    # Type message
                    message_box.send_keys(message)
                    time.sleep(1)
                    
                    # Find and click send button
                    send_selectors = [
                        "//span[@data-icon='send']",
                        "//span[@data-testid='send']",
                        "//button[@aria-label='Send']"
                    ]
                    
                    sent = False
                    for selector in send_selectors:
                        try:
                            send_btn = driver.find_element(By.XPATH, selector)
                            send_btn.click()
                            sent = True
                            time.sleep(2)
                            break
                        except:
                            continue
                    
                    if not sent:
                        # Try Enter key as fallback
                        message_box.send_keys(Keys.ENTER)
                        time.sleep(2)
                        
                except Exception as e:
                    return False, f"Error sending message: {str(e)}"
            
            # Wait for delay
            time.sleep(delay)
            
            return True, "Message sent successfully"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    except Exception as e:
        return False, f"Failed to open chat: {str(e)}"

def send_bulk_messages(contacts, message, attachment_path, delay):
    """Send bulk WhatsApp messages"""
    global sending_status
    
    sending_status['is_sending'] = True
    sending_status['total'] = len(contacts)
    sending_status['current_index'] = 0
    sending_status['success_count'] = 0
    sending_status['failed_count'] = 0
    sending_status['error_message'] = ''
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=./chrome_profile")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        
        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com")
        
        # Wait for user to scan QR code - check if already logged in
        sending_status['current_contact'] = "Waiting for QR code scan or checking login status..."
        
        # Wait and check if logged in (look for chat list or search box)
        wait = WebDriverWait(driver, 60)  # Give up to 60 seconds for QR scan
        try:
            # Check if already logged in by looking for search box or chat list
            search_box = wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")),
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'search')]")),
                    EC.presence_of_element_located((By.XPATH, "//div[@id='side']"))
                )
            )
            sending_status['current_contact'] = "Logged in successfully! Starting to send messages..."
            time.sleep(2)
        except:
            # If not logged in, wait for QR code scan
            sending_status['current_contact'] = "Please scan the QR code in the Chrome window..."
            # Wait for login indicator
            try:
                wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")),
                        EC.presence_of_element_located((By.XPATH, "//div[@id='side']"))
                    )
                )
                sending_status['current_contact'] = "Logged in successfully! Starting to send messages..."
                time.sleep(2)
            except:
                sending_status['is_sending'] = False
                sending_status['error_message'] = "QR code not scanned or login timeout"
                if driver:
                    driver.quit()
                return
        
        # Start sending messages
        for i, contact in enumerate(contacts):
            if not sending_status['is_sending']:
                break
            
            sending_status['current_index'] = i + 1
            sending_status['current_contact'] = f"Processing: {contact}"
            sending_status['error_message'] = ''
            
            success, error_msg = send_whatsapp_message(
                driver, contact, message, attachment_path, delay
            )
            
            if success:
                sending_status['success_count'] += 1
            else:
                sending_status['failed_count'] += 1
                sending_status['error_message'] = error_msg
        
        if driver:
            driver.quit()
        sending_status['is_sending'] = False
        sending_status['current_contact'] = "Completed!"
        
    except Exception as e:
        sending_status['is_sending'] = False
        sending_status['error_message'] = f"Error: {str(e)}"
        if driver:
            try:
                driver.quit()
            except:
                pass

# ---- WhatsApp Automation Endpoint ----
@app.route("/send", methods=["POST"])
def send_whatsapp():
    # Check API key
    if request.headers.get("X-API-KEY") != app.config['API_KEY']:
        return jsonify({"error": "Unauthorized"}), 403
    
    global sending_status
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data received"}), 400
    
    # Get data from request
    numbers = data.get("numbers", [])
    message = data.get("message", "")
    attachments = data.get("attachments", [])
    delay = max(15, int(data.get("delay", 15)))  # Minimum 15 seconds
    
    # Validation
    if len(numbers) == 0:
        return jsonify({"error": "Numbers are required"}), 400
    
    if message == "" and len(attachments) == 0:
        return jsonify({"error": "Message or attachments are required"}), 400
    
    # Check if already sending
    if sending_status['is_sending']:
        return jsonify({"error": "Already sending messages. Please wait."}), 400
    
    # Normalize phone numbers
    normalized_numbers = []
    for num in numbers:
        normalized = normalize_phone_number(num)
        if normalized:
            normalized_numbers.append(normalized)
    
    # Remove duplicates
    unique_numbers = remove_duplicates(normalized_numbers)
    
    if len(unique_numbers) == 0:
        return jsonify({"error": "No valid phone numbers found"}), 400
    
    # Handle attachments (if provided)
    attachment_path = None
    if attachments and len(attachments) > 0:
        # If attachment is a file path, use it directly
        # Otherwise, it should be uploaded first via /upload_attachment
        attachment_path = attachments[0] if isinstance(attachments[0], str) else None
        
        # Convert to absolute path if it's a relative path
        if attachment_path:
            if not os.path.isabs(attachment_path):
                attachment_path = os.path.abspath(attachment_path)
            
            # Verify file exists
            if not os.path.exists(attachment_path):
                return jsonify({
                    "error": f"Attachment file not found: {attachment_path}",
                    "hint": "Please upload the attachment first using /upload_attachment endpoint"
                }), 400
    
    # Start sending in background thread
    thread = threading.Thread(
        target=send_bulk_messages,
        args=(unique_numbers, message, attachment_path, delay)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True, 
        "message": "Messages scheduled successfully",
        "total_numbers": len(unique_numbers),
        "duplicates_removed": len(normalized_numbers) - len(unique_numbers)
    }), 200

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(sending_status)

@app.route('/stop', methods=['POST'])
def stop_sending():
    global sending_status
    sending_status['is_sending'] = False
    return jsonify({'success': True, 'message': 'Stopping...'})

if __name__ == '__main__':
    # Allow access from localhost and local network
    print("=" * 50)
    print("Bulk WhatsApp Sender - Starting Server")
    print("=" * 50)
    print("\nServer will be available at:")
    print("  - http://localhost:8080")
    print("  - http://127.0.0.1:8080")
    print("  - http://0.0.0.0:8080")
    print("\nTest route: http://localhost:8080/test")
    print("Main app: http://localhost:8080/app")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    print("\n")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=8080, threaded=True, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print("\nERROR: Port 5000 is already in use!")
            print("Please close the application using port 5000 or change the port in app.py")
        else:
            print(f"\nERROR: {str(e)}")
        raise

