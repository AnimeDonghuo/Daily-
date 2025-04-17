import requests
import sys

def check_health():
    try:
        response = requests.get('http://localhost:8080/health', timeout=5)
        if response.status_code == 200:
            print("Health check passed")
            sys.exit(0)
    except Exception:
        pass
    print("Health check failed")
    sys.exit(1)

if __name__ == '__main__':
    check_health()
