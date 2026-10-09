from typing import Any, Mapping, Protocol


class OncologyDataAdapter(Protocol):
    """Public contract implemented by a private operational integration."""

    def capabilities(self) -> dict[str, Any]:
        ...

    def fetch_one(self, dataset: str, params: Mapping[str, Any]) -> dict[str, Any] | None:
        ...

    def fetch_all(self, dataset: str, params: Mapping[str, Any]) -> list[dict[str, Any]]:
        ...

    def list_payers(self) -> list[dict[str, Any]]:
        ...

    def supports_payer(self, payer_id: int) -> bool:
        ...

    def health(self) -> dict[str, Any]:
        ...
