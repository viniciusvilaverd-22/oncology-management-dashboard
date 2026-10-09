import pytest

from app.integrations.registry import get_adapter


def test_public_repository_defaults_to_unavailable_adapter():
    adapter = get_adapter()
    caps = adapter.capabilities()

    assert caps["configured"] is False
    assert adapter.health()["status"] == "unavailable"

    with pytest.raises(ValueError):
        adapter.fetch_one("summary", {})
