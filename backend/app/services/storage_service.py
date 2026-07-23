import re
from urllib.parse import unquote, urlparse

from firebase_admin import storage

from app.core.firebase_app import get_firebase_app


class StorageFetchError(Exception):
    pass


def _blob_path_from_url(firebase_url: str) -> str:
    parsed = urlparse(firebase_url)
    match = re.search(r"/o/([^?]+)", parsed.path)
    if not match:
        raise StorageFetchError(f"Could not parse storage path from URL: {firebase_url}")
    return unquote(match.group(1))


def get_file_bytes(firebase_url: str) -> bytes:
    get_firebase_app()
    path = _blob_path_from_url(firebase_url)
    try:
        bucket = storage.bucket()
        blob = bucket.blob(path)
        return blob.download_as_bytes()
    except StorageFetchError:
        raise
    except Exception as exc:
        raise StorageFetchError(f"Failed to download '{path}' from Firebase Storage: {exc}") from exc
