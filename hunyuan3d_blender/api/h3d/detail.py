import requests
import uuid

from ..session import get_session

def get_creation_details(creations_id: str):
    """Fetches the details of a specific 3D creation task using its ID."""

    session = get_session()

    url = f"https://3d.hunyuan.tencent.com/api/3d/creations/detail?creationsId={creations_id}"

    headers = {
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": str(uuid.uuid4()),
        "accept": "application/json, text/plain, */*"
    }

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching creation details: {e}")
        return None
