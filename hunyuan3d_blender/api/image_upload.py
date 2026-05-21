import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Iterable

import requests
from PIL import Image


CATBOX_UPLOAD_URL = "https://catbox.moe/user/api.php"
UGUU_UPLOAD_URL = "https://uguu.se/upload"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)
_image_url_cache: dict[str, str] = {}


def _normalize_cache_key(key: str) -> str:
    return key.strip().casefold()


def _path_cache_key(file_path: str) -> str:
    return f"path:{str(Path(file_path).expanduser().resolve())}"


def _cache_keys(file_path: str, cache_keys: Iterable[str] | None = None) -> list[str]:
    keys = [_path_cache_key(file_path)]
    if cache_keys:
        keys.extend(key for key in cache_keys if key)
    return [_normalize_cache_key(key) for key in keys if key.strip()]


def clear_image_url_cache() -> None:
    _image_url_cache.clear()


def _safe_filename(file_path: str) -> str:
    filename = Path(file_path).name.replace(" ", "_")
    return filename or "hunyuan3d_upload.png"


def _content_type(file_path: str) -> str:
    guessed, _ = mimetypes.guess_type(file_path)
    return guessed or "application/octet-stream"


def prepare_upload_temp(original_path: str) -> str | None:
    """Re-encode the image as PNG and slightly alter pixels to avoid host rejections."""
    try:
        tmp = tempfile.NamedTemporaryFile(
            prefix="hunyuan3d_upload_",
            suffix=".png",
            delete=False,
        )
        tmp_path = tmp.name
        tmp.close()

        with Image.open(original_path) as image:
            prepared = image.convert("RGBA")
            width, height = prepared.size
            if width == 0 or height == 0:
                raise ValueError("Invalid image dimensions")

            first = prepared.getpixel((0, 0))
            last_xy = (width - 1, height - 1)
            last = prepared.getpixel(last_xy)
            prepared.putpixel((0, 0), (min(255, first[0] + 1), first[1], first[2], first[3]))
            prepared.putpixel(last_xy, (last[0], last[1], last[2], max(0, last[3] - 1)))
            prepared.save(tmp_path, format="PNG")

        return tmp_path
    except Exception as e:
        print(f"Failed to prepare image upload temp: {e}")
        try:
            os.remove(tmp_path)
        except (OSError, UnboundLocalError):
            pass
        return None


def upload_image_to_catbox(file_path: str, timeout: int = 120) -> str | None:
    if not os.path.isfile(file_path):
        print(f"Image upload failed: file does not exist: {file_path}")
        return None

    filename = _safe_filename(file_path)
    headers = {
        "Accept": "text/plain",
        "User-Agent": USER_AGENT,
    }

    try:
        with open(file_path, "rb") as file:
            files = {
                "fileToUpload": (filename, file, _content_type(file_path)),
            }
            data = {"reqtype": "fileupload"}
            response = requests.post(
                CATBOX_UPLOAD_URL,
                headers=headers,
                data=data,
                files=files,
                timeout=timeout,
            )
        response.raise_for_status()
        url = response.text.strip().splitlines()[0].strip()
        if url.startswith(("http://", "https://")):
            return url
        print(f"Catbox upload returned an unexpected response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"Catbox upload failed: {e}")

    return None


def upload_image_to_uguu(file_path: str, timeout: int = 120) -> str | None:
    if not os.path.isfile(file_path):
        print(f"Image upload failed: file does not exist: {file_path}")
        return None

    filename = _safe_filename(file_path)
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }

    try:
        with open(file_path, "rb") as file:
            files = {
                "files[]": (filename, file, _content_type(file_path)),
            }
            response = requests.post(
                UGUU_UPLOAD_URL,
                headers=headers,
                files=files,
                timeout=timeout,
            )
        response.raise_for_status()
        body = response.json()
        files_data = body.get("files") or body.get("data") or []
        if files_data:
            url = files_data[0].get("url") or files_data[0].get("link")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                return url
        for key in ("url", "link"):
            url = body.get(key)
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                return url
        print(f"Uguu upload returned an unexpected response: {str(body)[:200]}")
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Uguu upload failed: {e}")

    return None


def upload_image(file_path: str, cache_keys: Iterable[str] | None = None) -> str | None:
    """Upload an image to a public URL that Hunyuan can fetch."""
    keys = _cache_keys(file_path, cache_keys)
    for key in keys:
        url = _image_url_cache.get(key)
        if url:
            print(f"Reusing cached image URL for {key}")
            return url

    upload_path = prepare_upload_temp(file_path) or file_path
    try:
        url = upload_image_to_catbox(upload_path) or upload_image_to_uguu(upload_path)
        if url:
            for key in keys:
                _image_url_cache[key] = url
    finally:
        if upload_path != file_path:
            try:
                os.remove(upload_path)
            except OSError:
                pass

    return url
