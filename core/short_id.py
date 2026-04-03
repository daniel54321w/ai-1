import uuid
import hashlib

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def _encode_base62(num: int) -> str:
    if num == 0:
        return BASE62[0]
    result: list[str] = []
    while num:
        result.append(BASE62[num % 62])
        num //= 62
    return "".join(reversed(result))

def generate_short_id(uid: uuid.UUID | None = None, length: int = 7) -> str:
    """
    מייצר short_id ייחודי מ-UUID באמצעות SHA-256.
    עמיד בפני UUIDs דומים מאוד (כגון שורות seed עם הפרש של 1).
    """
    uid = uid or uuid.uuid4()
    hash_bytes = hashlib.sha256(uid.bytes).digest()
    num = int.from_bytes(hash_bytes[:8], "big")
    encoded = _encode_base62(num)
    return encoded[:length].ljust(length, "0")

def tool_url(short_id: str, base: str = "https://ai.co.il") -> str:
    return f"{base}/t/{short_id}"
