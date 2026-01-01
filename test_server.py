#!/usr/bin/env python
"""
Simple test script to verify Flask is working
Run this to test if Flask can serve pages correctly
"""
from flask import Flask, jsonify
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Flask Test Server - Working!</h1><p>If you see this, Flask is working correctly.</p>"

@app.route('/test')
def test():
    return jsonify({'status': 'success', 'message': 'Flask test successful'})

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'ok',
        'python_version': sys.version,
        'flask_working': True
    })

if __name__ == '__main__':
    print("Starting Flask Test Server...")
    print("Access at: http://localhost:5000")
    print("Test route: http://localhost:5000/test")
    print("API route: http://localhost:5000/api/status")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

