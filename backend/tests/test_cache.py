from app.services import cache


def test_cache_reuses_value_until_ttl_expires(monkeypatch):
    cache._CACHE.clear()
    now = [100.0]
    monkeypatch.setattr(cache, "monotonic", lambda: now[0])

    calls = []

    def loader():
        calls.append(1)
        return {"value": len(calls)}

    key = ("demo", "same-query")

    first = cache.get_or_set_cache(key, 60, loader)
    second = cache.get_or_set_cache(key, 60, loader)

    assert first == {"value": 1}
    assert second == first
    assert len(calls) == 1

    now[0] += 61
    third = cache.get_or_set_cache(key, 60, loader)

    assert third == {"value": 2}
    assert len(calls) == 2
