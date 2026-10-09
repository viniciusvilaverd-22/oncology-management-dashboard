from time import monotonic
from threading import RLock, Lock

_CACHE = {}
_LOCK = RLock()

MAX_CACHE_ENTRIES = 500
_LOCK_STRIPES = [Lock() for _ in range(64)]


def _prune():
    if len(_CACHE) <= MAX_CACHE_ENTRIES:
        return

    oldest = sorted(
        _CACHE.items(),
        key=lambda item: item[1][0]
    )

    excess = len(_CACHE) - MAX_CACHE_ENTRIES

    for key, _ in oldest[:excess]:
        _CACHE.pop(key, None)


def get_cache(key, ttl_seconds=60):
    now = monotonic()

    with _LOCK:
        item = _CACHE.get(key)

        if not item:
            return None

        created, value = item

        if now - created > ttl_seconds:
            _CACHE.pop(key, None)
            return None

        return value


def set_cache(key, value):
    with _LOCK:
        _CACHE[key] = (monotonic(), value)
        _prune()

    return value


def get_or_set_cache(key, ttl_seconds, loader):
    # Primeira tentativa: caminho rápido.
    hit = get_cache(key, ttl_seconds)
    if hit is not None:
        return hit

    # Requisições da mesma chave caem na mesma trava.
    stripe = _LOCK_STRIPES[hash(key) % len(_LOCK_STRIPES)]

    with stripe:
        # Outra requisição pode ter preenchido o cache enquanto esperávamos.
        hit = get_cache(key, ttl_seconds)
        if hit is not None:
            return hit

        value = loader()
        return set_cache(key, value)
