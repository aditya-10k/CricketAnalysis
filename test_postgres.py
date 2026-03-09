import requests
import time

API_URL = "http://localhost:8000"

def test_api():
    print("Testing API connectivity...")
    try:
        # Check docs or root
        resp = requests.get(f"{API_URL}/docs")
        if resp.status_code == 200:
            print("API is running (Docs available)")
        else:
            print(f" API returned status {resp.status_code}")
            
        # Test replacement endpoint
        print("Testing replacement endpoint...")
        payload = {"player": "Virat Kohli", "top_n": 1}
        resp = requests.post(f"{API_URL}/api/replacement/find", json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f" Success! Found: {data}")
        elif resp.status_code == 404:
             print(" API reachable (404 for player is expected if DB empty/player missing)")
        else:
            print(f" API Error: {resp.text}")

    except Exception as e:
        print(f" Connection failed: {e}")

if __name__ == "__main__":
    time.sleep(2) 
    test_api()
