from typing import Any, Mapping


class IntegrationUnavailableError(ValueError):
    pass


class UnavailableDataAdapter:
    """Safe default used by the public repository.

    The operational ERP adapter is deliberately not shipped here.
    """

    _MESSAGE = (
        "O adapter operacional privado não está instalado nesta edição pública. "
        "Use o modo demo sintético ou forneça um adapter compatível fora deste repositório."
    )

    def capabilities(self) -> dict[str, Any]:
        return {
            "configured": False,
            "pacientes": False,
            "custo_medicamento": False,
            "recebimento_efetivo": False,
            "fonte_recebimento": "Adapter operacional privado não incluído.",
            "semantica_recebimento": "Evento financeiro de recebimento fornecido pelo adapter privado.",
        }

    def _raise(self):
        raise IntegrationUnavailableError(self._MESSAGE)

    def fetch_one(self, dataset: str, params: Mapping[str, Any]):
        self._raise()

    def fetch_all(self, dataset: str, params: Mapping[str, Any]):
        self._raise()

    def list_payers(self) -> list[dict[str, Any]]:
        return []

    def supports_payer(self, payer_id: int) -> bool:
        return False

    def health(self) -> dict[str, Any]:
        return {
            "status": "unavailable",
            "configured": False,
            "integration": "private-operational-adapter",
        }


def create_adapter():
    return UnavailableDataAdapter()
