from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from .config import get_settings


class EncryptionError(RuntimeError):
    pass


@lru_cache
def _get_fernet() -> Fernet:
    settings = get_settings()
    key = settings.app_encryption_key
    if not key:
        raise EncryptionError(
            "APP_ENCRYPTION_KEY is not configured; cannot encrypt secrets."
        )
    return Fernet(key)


def encrypt_secret(value: str) -> str:
    if not value:
        raise EncryptionError("Cannot encrypt empty secret value.")
    return _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    try:
        return _get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise EncryptionError("Failed to decrypt secret.") from exc
