#!/usr/bin/env python3
"""
Verification script to check if everything is set up correctly
"""
import sys
import os

print("=" * 60)
print("Bulk WhatsApp Sender - Setup Verification")
print("=" * 60)
print()

# Check Python version
print("1. Checking Python version...")
print(f"   Python: {sys.version}")
if sys.version_info < (3, 8):
    print("   ⚠️  WARNING: Python 3.8+ recommended")
else:
    print("   ✅ Python version OK")
print()

# Check required packages
print("2. Checking required packages...")
required_packages = [
    'flask',
    'pandas',
    'selenium',
    'openpyxl',
    'webdriver_manager',
    'werkzeug'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package} installed")
    except ImportError:
        print(f"   ❌ {package} NOT installed")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   ⚠️  Missing packages: {', '.join(missing_packages)}")
    print("   Run: pip install -r requirements.txt")
else:
    print("\n   ✅ All required packages installed")
print()

# Check file structure
print("3. Checking file structure...")
files_to_check = [
    ('app.py', 'Main application file'),
    ('templates/index.html', 'HTML template'),
    ('requirements.txt', 'Dependencies file'),
    ('uploads', 'Uploads directory')
]

all_files_ok = True
for filepath, description in files_to_check:
    if os.path.exists(filepath):
        print(f"   ✅ {description}: {filepath}")
    else:
        print(f"   ❌ {description} NOT FOUND: {filepath}")
        all_files_ok = False

if not all_files_ok:
    print("\n   ⚠️  Some files are missing!")
else:
    print("\n   ✅ File structure OK")
print()

# Test Flask app import
print("4. Testing Flask app import...")
try:
    sys.path.insert(0, '.')
    from app import app
    print("   ✅ Flask app imported successfully")
    
    # Check routes
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    print(f"   ✅ Found {len(routes)} routes:")
    for route in routes[:5]:  # Show first 5
        print(f"      - {route}")
    if len(routes) > 5:
        print(f"      ... and {len(routes) - 5} more")
    
except Exception as e:
    print(f"   ❌ Error importing app: {str(e)}")
    import traceback
    traceback.print_exc()
print()

# Check template file
print("5. Checking template file...")
template_path = os.path.join('templates', 'index.html')
if os.path.exists(template_path):
    size = os.path.getsize(template_path)
    print(f"   ✅ Template found: {template_path} ({size} bytes)")
else:
    print(f"   ❌ Template NOT found: {template_path}")
print()

# Summary
print("=" * 60)
print("Verification Complete!")
print("=" * 60)
print()
print("To start the application:")
print("  - Windows: Double-click run.bat or start_app.bat")
print("  - Mac/Linux: python3 app.py")
print()
print("Then open in browser:")
print("  - http://localhost:5000")
print("  - http://127.0.0.1:5000")
print()
print("If you get 403 error:")
print("  1. Try http://localhost:5000 (not 127.0.0.1)")
print("  2. Try different browser or incognito mode")
print("  3. Check FIX_403_ERROR.md for detailed solutions")
print()

