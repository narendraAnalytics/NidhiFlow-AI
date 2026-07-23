import threading

import firebase_admin
from firebase_admin import credentials

from app.core.config import FIREBASE_STORAGE_BUCKET

_app = None
_app_lock = threading.Lock()


def get_firebase_app():
    """Single shared entry point for firebase_admin.initialize_app(). The
    default app can only be initialized once per process -- every caller
    that needs Firebase Admin (Storage, Auth token verification, ...) must
    go through this function rather than calling initialize_app() itself.
    """
    global _app
    if _app is None:
        with _app_lock:
            if _app is None:
                try:
                    _app = firebase_admin.get_app()
                except ValueError:
                    _app = firebase_admin.initialize_app(
                        credentials.ApplicationDefault(),
                        {"storageBucket": FIREBASE_STORAGE_BUCKET},
                    )
    return _app
