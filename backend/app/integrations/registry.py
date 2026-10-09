from functools import lru_cache
from importlib import import_module

from app.config import settings
from app.integrations.unavailable import create_adapter as create_unavailable_adapter

_REQUIRED_METHODS = (
    "capabilities",
    "fetch_one",
    "fetch_all",
    "list_payers",
    "supports_payer",
    "health",
)


def _load_factory(spec: str):
    if ":" not in spec:
        raise RuntimeError("DATA_ADAPTER deve usar o formato pacote.modulo:factory")
    module_name, factory_name = spec.split(":", 1)
    module = import_module(module_name)
    factory = getattr(module, factory_name, None)
    if not callable(factory):
        raise RuntimeError(f"Factory de adapter inválida: {spec}")
    return factory


@lru_cache(maxsize=1)
def get_adapter():
    spec = (settings.data_adapter or "").strip()
    adapter = create_unavailable_adapter() if not spec else _load_factory(spec)()

    missing = [name for name in _REQUIRED_METHODS if not callable(getattr(adapter, name, None))]
    if missing:
        raise RuntimeError(f"Adapter incompatível; métodos ausentes: {', '.join(missing)}")
    return adapter


def reset_adapter_cache():
    get_adapter.cache_clear()
