from datetime import date

import pytest

from app.services import onco


def test_period_validation_rejects_invalid_ranges():
    with pytest.raises(ValueError):
        onco.binds(date(2026, 10, 2), date(2026, 10, 1))

    with pytest.raises(ValueError):
        onco.binds(date(2025, 1, 1), date(2026, 1, 2))


def test_sector_filter_accepts_unique_positive_ids():
    assert onco._parse_setores("113, 7, 113") == [113, 7]

    with pytest.raises(ValueError):
        onco._parse_setores("113,abc")

    with pytest.raises(ValueError):
        onco._parse_setores("0")


def test_receipt_audit_keeps_open_and_denied_balances_separate(monkeypatch):
    rows = [
        {
            "status_recebimento": "RECEBIDA",
            "qt_eventos_acumulados": 1,
            "vl_faturado": 1000,
            "vl_recebido_base_periodo": 1000,
            "vl_glosa_periodo": 0,
            "vl_saldo_estimado": 0,
            "vl_saldo_glosado": 0,
            "vl_saldo_financeiro_aberto": 0,
        },
        {
            "status_recebimento": "PARCIALMENTE_RECEBIDA_COM_GLOSA",
            "qt_eventos_acumulados": 2,
            "vl_faturado": 1200,
            "vl_recebido_base_periodo": 800,
            "vl_glosa_periodo": 100,
            "vl_saldo_estimado": 400,
            "vl_saldo_glosado": 100,
            "vl_saldo_financeiro_aberto": 300,
        },
    ]

    monkeypatch.setattr(onco, "get_pagamentos_contas", lambda *_args, **_kwargs: rows)

    result = onco.get_auditoria_recebimentos_resumo(
        date(2026, 9, 1),
        date(2026, 9, 30),
    )

    assert result["qt_contas"] == 2
    assert result["qt_recebidas"] == 1
    assert result["qt_parcialmente_recebidas_com_glosa"] == 1
    assert result["qt_multiplos_recebimentos"] == 1
    assert result["vl_saldo_total_estimado"] == 400
    assert result["vl_saldo_glosado"] == 100
    assert result["vl_saldo_financeiro_aberto"] == 300
