import uuid

import requests

from ..session import get_session
from .sign import signed_url

DEFAULT_MODEL_TYPE = "text2ModelV3.1"
DEFAULT_FACE_COUNT = 1_500_000
DEFAULT_SCENE_TYPE = "playGround3D-2.0"
GENERATIONS_URL = "https://3d.hunyuan.tencent.com/api/3d/creations/generations"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)


def _build_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": str(uuid.uuid4()),
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "Origin": "https://3d.hunyuan.tencent.com",
        "Referer": "https://3d.hunyuan.tencent.com/",
        "User-Agent": USER_AGENT,
    }


def generate_3d_model(
    prompt: str,
    title: str,
    style: str = "",
    count: int = 4,
    enable_pbr: bool = True,
    enable_low_poly: bool = False,
    *,
    scene_type: str = DEFAULT_SCENE_TYPE,
    model_type: str = DEFAULT_MODEL_TYPE,
    face_count: int = DEFAULT_FACE_COUNT,
) -> str | None:
    """Send a text-to-3D generation request to the Hunyuan 3D API."""
    session = get_session()

    payload = {
        "prompt": prompt,
        "title": title,
        "style": style,
        "sceneType": scene_type,
        "modelType": model_type,
        "count": count,
        "faceCount": face_count,
        "enable_pbr": enable_pbr,
        "enableLowPoly": enable_low_poly,
    }

    url = signed_url(GENERATIONS_URL)
    headers = _build_headers()

    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()
        details = response.json()
        print(details)
        return details.get("creationsId")
    except requests.exceptions.RequestException as e:
        print(f"Error during 3D model generation request: {e}")
        response = getattr(e, "response", None)
        if response is not None:
            print(f"Response body: {response.text}")
        return None
