import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import time

BASE_URL = "http://codechicks.vercel.app/auth"

def request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = None
    if data:
        encoded_data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Failed to connect to {url}: {e}")
        return 0, None

def run_tests():
    print("Waiting for server to be ready...")
    for _ in range(10):
        try:
            urllib.request.urlopen("http://localhost:8000/api/status")
            print("Server is up!")
            break
        except:
            time.sleep(1)
    else:
        print("Server failed to start.")
        sys.exit(1)

    print("\n--- Testing Registration ---")
    email = f"test_{int(time.time())}@example.com"
    password = "secretpassword"
    
    status, body = request("POST", "/register", {"email": email, "password": password})
    if status == 200 and "access_token" in body:
        print(f"✅ Registration Successful. Token received.")
        token = body["access_token"]
    else:
        print(f"❌ Registration Failed. Status: {status}, Body: {body}")
        sys.exit(1)

    print("\n--- Testing Login ---")
    status, body = request("POST", "/login", {"email": email, "password": password})
    if status == 200 and "access_token" in body:
        print(f"✅ Login Successful. Token received.")
        token = body["access_token"] # Update token just in case
    else:
        print(f"❌ Login Failed. Status: {status}, Body: {body}")
        sys.exit(1)

    print("\n--- Testing Protected Route (/me) ---")
    status, body = request("GET", "/me", token=token)
    if status == 200 and body.get("email") == email:
        print(f"✅ Protected Route Access Successful. User: {body['email']}")
    else:
        print(f"❌ Protected Route Failed. Status: {status}, Body: {body}")
        sys.exit(1)

    print("\n--- Testing Invalid Token ---")
    status, body = request("GET", "/me", token="invalid_token")
    if status == 401:
        print(f"✅ Invalid Token correctly rejected.")
    else:
        print(f"❌ Invalid Token check failed. Status: {status} (Expected 401)")

if __name__ == "__main__":
    run_tests()
