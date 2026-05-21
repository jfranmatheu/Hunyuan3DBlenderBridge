import hashlib
import hmac
import secrets
import string
import time
from typing import Dict
from urllib.parse import urlencode

_KEY_MATERIAL = bytes([122, 59, 92, 165, 30, 79, 166, 139, 142, 129, 139, 89, 219, 131, 101, 204])
_XOR_MASK = bytes([122, 59, 92, 45, 30, 79, 106, 139, 156, 13, 46, 63, 74, 91, 108, 125])
_ROTATIONS = (3, 5, 2, 7, 1, 4, 6, 2, 5, 3, 1, 4, 2, 6, 3, 5)
_PERMUTATION = (14, 11, 13, 9, 15, 10, 12, 8, 6, 3, 5, 1, 7, 2, 4, 0)
_NONCE_ALPHABET = string.ascii_letters + string.digits


def _derive_signing_key(key_material: bytes) -> bytes:
    xored = bytes(key_material[i] ^ _XOR_MASK[i] for i in range(16))
    rotated = bytearray(16)
    for i in range(16):
        rotation = _ROTATIONS[i]
        rotated[i] = (xored[i] << rotation | xored[i] >> (8 - rotation)) & 0xFF
    permuted = bytearray(16)
    for i in range(16):
        permuted[i] = rotated[_PERMUTATION[i]]
    zero_index = permuted.index(0) if 0 in permuted else 16
    return bytes(permuted[:zero_index])


def _build_sign_message(params: Dict[str, str]) -> str:
    pairs = sorted(
        ((key, str(value)) for key, value in params.items() if value is not None and value != ""),
        key=lambda item: item[0],
    )
    return "&".join(f"{key}={value}" for key, value in pairs)


def build_signed_query_params(
    params: Dict[str, str] | None = None,
    *,
    nonce_length: int = 16,
) -> Dict[str, str]:
    """Build timestamp, nonce, and sign query params for Hunyuan 3D API requests."""
    signed = dict(params or {})
    signed["timestamp"] = str(int(time.time()))
    signed["nonce"] = "".join(secrets.choice(_NONCE_ALPHABET) for _ in range(nonce_length))
    signing_key = _derive_signing_key(_KEY_MATERIAL)
    message = _build_sign_message(signed)
    signed["sign"] = hmac.new(signing_key, message.encode(), hashlib.sha256).hexdigest()
    return signed


def signed_url(base_url: str, params: Dict[str, str] | None = None) -> str:
    query = urlencode(build_signed_query_params(params))
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{query}"
