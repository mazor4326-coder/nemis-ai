import urllib.request
import json

req = urllib.request.Request(
    'http://127.0.0.1:5000/assistant',
    data=json.dumps({"user_id": "1477103854", "lesson_number": 1}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
