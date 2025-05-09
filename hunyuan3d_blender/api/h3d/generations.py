import requests
import uuid

from ..session import get_session

def generate_3d_model(prompt: str, title: str, style: str = "", count: int = 4, enable_pbr: bool = True, enable_low_poly: bool = False) -> str | None:
    """Sends a request to the Hunyuan 3D API to generate a 3D model based on a text prompt.

        Arguments:
            prompt: str - The prompt to generate the 3D model from.
            style: str - The style to use for the 3D model. (e.g. "china_style") Use "" for default.
            sceneType: str - The scene type to use for the 3D model.
            modelType: str - The model type to use for the 3D model.
            count: int - The number of 3D models to generate.
            enable_pbr: bool - Whether to enable PBR for the 3D model.
            enable_low_poly: bool - Whether to enable low poly for the 3D model.
    """

    session = get_session()

    url = "https://3d.hunyuan.tencent.com/api/3d/creations/generations"

    payload = {
        "prompt": prompt,
        "title": title,  # usually the prompt
        "style": style,  # "china_style", ...
        "sceneType": "playGround3D-2.0",
        "modelType": "modelCreationV2.5",
        "count": count,
        "enable_pbr": enable_pbr,
        "enableLowPoly": enable_low_poly
    }

    trace_id = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/json",
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": trace_id,
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "138",
        "content-type": "application/json",
        "Origin": "https://3d.hunyuan.tencent.com", # Often required for POST requests
        "Referer": "https://3d.hunyuan.tencent.com/", # Mimic browser behavior
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        details = response.json()
        print(details)
        return details["creationsId"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during 3D model generation request: {e}")
        return None
