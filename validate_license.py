import requests
import sys

def validate_license(license_key):
    """
    Validates the license key against the footydjLicensify API.
    """
    # URL configured based on the user's dashboard settings
    API_URL = "https://footydj-licence.vercel.app/api/validate"
    
    try:
        response = requests.post(API_URL, json={
            "key": license_key
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                print(f"✅ Success: License is valid until {data.get('expires_at')}")
                return True
            else:
                print(f"❌ Error: {data.get('message', 'License invalid')}")
                return False
        else:
            print(f"❌ Server Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Connection Error: {e}")
        return False

# Example Usage
if __name__ == "__main__":
    # Replace with the user's input key
    print("--- footydjLicensify Validator ---")
    user_key = input("Enter License Key: ").strip()
    
    if validate_license(user_key):
        print("Starting Application...")
        # Start your main application logic here
    else:
        print("Please purchase a valid license to continue.")
        sys.exit(1)
