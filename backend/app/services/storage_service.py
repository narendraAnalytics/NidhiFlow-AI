import re
import threading
from urllib.parse import unquote, urlparse

import firebase_admin
from firebase_admin import credentials, storage

from app.core.config import FIREBASE_STORAGE_BUCKET

_app = None
_app_lock = threading.Lock()


class StorageFetchError(Exception):
    pass


def _get_app():
    global _app
    if _app is None:
        with _app_lock:
            if _app is None:
                _app = firebase_admin.initialize_app(
                    credentials.ApplicationDefault(),
                    {"storageBucket": FIREBASE_STORAGE_BUCKET},
                )
    return _app


def _blob_path_from_url(firebase_url: str) -> str:
    parsed = urlparse(firebase_url)
    match = re.search(r"/o/([^?]+)", parsed.path)
    if not match:
        raise StorageFetchError(f"Could not parse storage path from URL: {firebase_url}")
    return unquote(match.group(1))


def get_file_bytes(firebase_url: str) -> bytes:
    _get_app()
    path = _blob_path_from_url(firebase_url)
    try:
        bucket = storage.bucket()
        blob = bucket.blob(path)
        return blob.download_as_bytes()
    except StorageFetchError:
        raise
    except Exception as exc:
        raise StorageFetchError(f"Failed to download '{path}' from Firebase Storage: {exc}") from exc
