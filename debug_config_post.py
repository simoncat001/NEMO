import requests
import json
import os

# Disable proxy
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

BASE_URL = "http://localhost:8000/api/v1"

def login():
    url = f"{BASE_URL}/auth/login/json"
    payload = {"username": "admin", "password": "admin"}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Login successful")
            return response.json().get("access_token")
        else:
            print(f"Login failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def create_config(token):
    url = f"{BASE_URL}/configurations/"
    # Payload mimicking what the frontend sends
    payload = {
        "name": "Test Config",
        "tool_id": 1,
        "enabled": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    token = login()
    if token:
        create_config(token)

