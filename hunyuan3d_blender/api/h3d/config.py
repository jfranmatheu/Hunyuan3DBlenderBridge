import requests
import uuid
from typing import Dict, Any, Optional

from ..session import get_session

def get_h3d_config() -> Dict[str, Any] | None:
    """Fetches the main configuration data from the Hunyuan 3D API."""

    session = get_session()

    url = "https://3d.hunyuan.tencent.com/api/3d/config"

    headers = {
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": str(uuid.uuid4()),
        "accept": "application/json, text/plain, */*"
    }

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        # Basic validation - check if it's a dictionary
        if data and isinstance(data, dict):
            return data
        else:
            print(f"❌ Error: Unexpected response format from config endpoint: {data}")
            return None

    except requests.exceptions.Timeout:
        print(f"❌ Error: Request to {url} timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching H3D config: {e}")
        return None
    except Exception as e:
        # Catch potential JSON decoding errors or other unexpected issues
        print(f"❌ An unexpected error occurred while fetching config: {e}")
        return None

# Example usage:
# if __name__ == "__main__":
#     config_data = get_h3d_config()
#     if config_data:
#         print("✅ Successfully fetched H3D config.")
#         # Example: Print available texture styles
#         texture_styles = config_data.get('styleConfig', {}).get('textureStyle', [])
#         print("\nAvailable Texture Styles:")
#         for style in texture_styles:
#             print(f"  - Name: {style.get('styleName')}, Key: {style.get('style')}")
#     else:
#         print("❌ Failed to fetch H3D config.")
