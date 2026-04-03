import uuid

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
    uid = uid or uuid.uuid4()
    encoded = _encode_base62(uid.int)
    mid  = len(encoded) // 2
    half = length // 2
    short = encoded[mid - half : mid - half + length]
    if len(short) < length:
        short = encoded[:length].ljust(length, "0")
    return short

def tool_url(short_id: str, base: str = "https://ai.co.il") -> str:
    return f"{base}/t/{short_id}"
