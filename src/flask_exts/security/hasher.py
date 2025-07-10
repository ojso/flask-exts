from hashlib import blake2b
from hmac import compare_digest


class Blake2bHasher:
    """
    Hash context for string hashing and verification.
    """

    digest_size = 16

    def __init__(self, key):
        self.key = key if isinstance(key, bytes) else key.encode("utf-8")

    def hash(self, data: str) -> str:
        h = blake2b(digest_size=self.digest_size, key=self.key)
        h.update(data.encode("utf-8"))
        return h.hexdigest()

    def verify(self, data: str, hashed_data: str) -> bool:
        new_hash = self.hash(data)
        return compare_digest(new_hash, hashed_data)
