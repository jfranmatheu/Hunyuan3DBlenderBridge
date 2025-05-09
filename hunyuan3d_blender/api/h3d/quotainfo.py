import requests
import uuid
from dataclasses import dataclass

from ..session import get_session

@dataclass
class QuotaInfo:
    date: str
    totalQuota: int
    alarmQuota: int
    remainQuota: int
    consumeQuota: int
    userInviteQuota: int
    showUserInviteQuotaTag: bool
    perUserInviteQuotaCount: int
    maxUserInviteQuota: int

def get_quota_info(sceneType: str = "3dCreations") -> QuotaInfo | None:
    """Fetches quota information from the Hunyuan 3D API and returns it as a QuotaInfo dataclass."""

    session = get_session()

    url = "https://3d.hunyuan.tencent.com/api/3d/quotainfo"

    payload = {
        "sceneType": sceneType
    }

    headers = {
        "Content-Type": "application/json",
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": str(uuid.uuid4()),
        "accept": "application/json, text/plain, */*"
    }

    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        
        # Check if the response data is valid and contains expected keys
        if data and isinstance(data, dict) and 'date' in data: # Basic check
            return QuotaInfo(**data)
        else:
            print(f"❌ Error: Unexpected response format from quota info endpoint: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching quota info: {e}")
        return None
    except (TypeError, KeyError) as e:
        print(f"❌ Error parsing quota info response or missing key: {e} - Response: {data}")
        return None
