# API Usage Example

## Backend (Flask)

The `/send` endpoint is protected with API key authentication:

```python
@app.route("/send", methods=["POST"])
def send_whatsapp():
    # Check API key
    if request.headers.get("X-API-KEY") != app.config['API_KEY']:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    numbers = data.get("numbers", [])
    message = data.get("message", "")
    attachments = data.get("attachments", [])
    
    # ... WhatsApp automation code ...
    
    return jsonify({"success": True, "message": "Messages scheduled successfully"}), 200
```

## Frontend (JavaScript)

### Using Fetch API

```javascript
fetch("http://localhost:5000/send", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-KEY": "YOUR_SECRET_KEY"  // Must match the API key in app.py
  },
  body: JSON.stringify({
    numbers: ["+919876543210", "+1234567890"],
    message: "Hello from Bulk WhatsApp Sender!",
    attachments: []  // Optional: array of file paths
  })
})
  .then(res => res.json())
  .then(data => {
    console.log(data);
    if (data.success) {
      console.log("Messages scheduled successfully!");
    } else {
      console.error("Error:", data.error);
    }
  })
  .catch(err => console.error("Request failed:", err));
```

### Example with Error Handling

```javascript
async function sendBulkMessages(numbers, message, attachments = []) {
  try {
    const response = await fetch("http://localhost:5000/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": "YOUR_SECRET_KEY"
      },
      body: JSON.stringify({
        numbers: numbers,
        message: message,
        attachments: attachments
      })
    });

    const data = await response.json();

    if (response.status === 403) {
      console.error("Unauthorized: Check your API key");
      return { error: "Unauthorized" };
    }

    if (response.status === 400) {
      console.error("Bad Request:", data.error);
      return { error: data.error };
    }

    if (data.success) {
      console.log("Success:", data.message);
      return { success: true, data: data };
    }

    return { error: data.error || "Unknown error" };
  } catch (error) {
    console.error("Network error:", error);
    return { error: error.message };
  }
}

// Usage
sendBulkMessages(
  ["+919876543210", "+1234567890"],
  "Hello! This is a test message.",
  []
);
```

## API Key Configuration

1. **Change the API key in `app.py`:**
   ```python
   app.config['API_KEY'] = 'YOUR_SECRET_KEY'  # Change this to your actual API key
   ```

2. **Update the frontend to use the same key:**
   ```javascript
   headers: {
     "X-API-KEY": "YOUR_SECRET_KEY"  // Must match app.py
   }
   ```

## Request Format

```json
{
  "numbers": ["+919876543210", "+1234567890"],
  "message": "Your message here",
  "attachments": []  // Optional
}
```

## Response Format

### Success (200)
```json
{
  "success": true,
  "message": "Messages scheduled successfully",
  "total_numbers": 2,
  "duplicates_removed": 0
}
```

### Error - Unauthorized (403)
```json
{
  "error": "Unauthorized"
}
```

### Error - Bad Request (400)
```json
{
  "error": "Numbers are required"
}
```

## Testing with cURL

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

## Testing with Python

```python
import requests

url = "http://localhost:5000/send"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "YOUR_SECRET_KEY"
}
data = {
    "numbers": ["+919876543210"],
    "message": "Test message",
    "attachments": []
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

