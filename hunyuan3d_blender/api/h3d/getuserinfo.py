import requests
import uuid

from ..session import get_session

def get_user_info():
    """Fetches user information from the Hunyuan 3D API."""

    session = get_session()

    url = "https://3d.hunyuan.tencent.com/api/3d/getuserinfo"

    headers = {
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": str(uuid.uuid4()),
        "accept": "application/json, text/plain, */*"
        # No Content-Type needed for GET request without body
    }

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching user info: {e}")
        return None
