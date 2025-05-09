import requests
import uuid
import datetime

from ..session import get_session

def get_creations_list(limit: int = 20, offset: int = 0):
    """Fetches a list of 3D creation tasks from the Hunyuan 3D API."""

    session = get_session()

    url = "https://3d.hunyuan.tencent.com/api/3d/creations/list"

    payload = {
        "limit": limit,
        "offset": offset,
        "sceneTypeList": []
    }

    headers = {
        "Content-Type": "application/json",
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": str(uuid.uuid4()),
        "cache-control": "no-cache",
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"), # Format similar to JS Date().toISOString()
        "accept": "application/json, text/plain, */*"
    }

    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching creations list: {e}")
        return None
