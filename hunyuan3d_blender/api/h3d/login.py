import requests
import uuid

from ..session import get_session

def login_with_email(email: str, verification_code: str) -> bool:
    """Attempts to log in to Hunyuan 3D using email and verification code, storing cookies in the session.

    Args:
        email: The email address for login.
        verification_code: The verification code received via email.

    Returns:
        True if the login request returns a 200 status code, False otherwise.
    """

    session = get_session()

    url = "https://3d.hunyuan.tencent.com/api/login/email/login"

    payload = {
        "email": email,
        "verificationCode": verification_code
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": str(uuid.uuid4()),
        "Origin": "https://3d.hunyuan.tencent.com", # Often required for POST requests
        "Referer": "https://3d.hunyuan.tencent.com/", # Mimic browser behavior
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = session.post(url, headers=headers, json=payload, timeout=15)
        
        # Check for successful status code (e.g., 200 OK)
        if response.status_code == 200:
            print(f"✅ Login successful for {email}. Cookies set in session.")
            # Optionally parse response.json() if it contains useful info
            # login_data = response.json() 
            return True
        else:
            print(f"❌ Login failed for {email}. Status: {response.status_code}, Response: {response.text}")
            response.raise_for_status() # Raise exception for non-200 codes after logging
            return False # Should not be reached if raise_for_status() triggers

    except requests.exceptions.Timeout:
        print(f"❌ Error: Login request to {url} timed out.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during login request: {e}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during login: {e}")
        return False

# Example Usage (requires a valid verification code process):
# if __name__ == "__main__":
#     login_session = requests.Session()
#     user_email = "your_temp_email@example.com" # Replace with actual email
#     code = input(f"Enter verification code sent to {user_email}: ")
#     
#     if login_with_email(login_session, user_email, code):
#         print("Login successful! Session has cookies.")
#         # Now you can use login_session for other authenticated requests, e.g.:
#         # from .quotainfo import get_quota_info
#         # quota = get_quota_info(login_session)
#         # if quota:
#         #     print(f"Remaining Quota: {quota.remainQuota}")
#     else:
#         print("Login failed.")
