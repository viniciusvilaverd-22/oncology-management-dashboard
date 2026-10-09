from datetime import date, timedelta

from app.integrations.registry import get_adapter
from app.services.cache import get_cache, get_or_set_cache, set_cache

MAX_DAYS = 365


def binds(data_inicio: date, data_fim: date):
    if data_fim < data_inicio:
        raise ValueError("data_fim não pode ser anterior a data_inicio")
    dias = (data_fim - data_inicio).days + 1
    if dias > MAX_DAYS:
        raise ValueError(f"Período máximo permitido nesta versão segura: {MAX_DAYS} dias.")
    return {"data_inicio": data_inicio, "data_fim": data_fim}


def _cached(name, data_inicio, data_fim, loader, ttl=60):
    key = (name, data_inicio.isoformat(), data_fim.isoformat())
    return get_or_set_cache(key, ttl, loader)


def _safe_float(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _delta_pct(current, previous):
    c = _safe_float(current)
    p = _safe_float(previous)
    if p == 0:
        return None if c else 0.0
    return round((c - p) / p * 100, 2)


def _one(dataset, params):
    return get_adapter().fetch_one(dataset, params)


def _all(dataset, params):
    return get_adapter().fetch_all(dataset, params)


def get_schema_capabilities():
    key = ("integration_capabilities_v1",)
    hit = get_cache(key, 3600)
    if hit is not None:
        return hit
    value = dict(get_adapter().capabilities() or {})
    value.setdefault("configured", True)
    value.setdefault("pacientes", False)
    value.setdefault("custo_medicamento", False)
    value.setdefault("recebimento_efetivo", False)
    value.setdefault("fonte_recebimento", "Evento financeiro fornecido pelo adapter privado.")
    value.setdefault(
        "semantica_recebimento",
        "Data registrada pelo evento financeiro; não é inferida a partir da competência.",
    )
    value["periodo_maximo_dias"] = MAX_DAYS
    return set_cache(key, value)


def _require_patient_support():
    caps = get_schema_capabilities()
    if not caps.get("pacientes"):
        raise ValueError("O adapter configurado não fornece a dimensão de pacientes.")
    return caps


def _require_receipt_support():
    caps = get_schema_capabilities()
    if not caps.get("recebimento_efetivo"):
        raise ValueError("O adapter configurado não fornece eventos financeiros de recebimento.")
    return caps


def get_resumo(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)
    return _cached("resumo_v6", data_inicio, data_fim, lambda: _one("summary", b), 300)


def get_financeiro(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)

    def load():
        row = _one("production_financial_summary", b) or {}
        faturado = _safe_float(row.get("vl_faturado"))
        remetido = _safe_float(row.get("vl_remetido"))
        glosa_bruta = _safe_float(row.get("vl_glosa_bruta"))
        glosa_liquida = _safe_float(row.get("vl_glosa_liquida"))
        row["pct_remetido_faturado"] = round((remetido / faturado * 100), 2) if faturado else 0
        row["pct_glosa_bruta_remetido"] = round((glosa_bruta / remetido * 100), 4) if remetido else 0
        row["pct_glosa_liquida_remetido"] = round((glosa_liquida / remetido * 100), 4) if remetido else 0
        row["nota_pagamento"] = (
            "Status operacional de lote e evento financeiro de recebimento são conceitos distintos."
        )
        row["semantica_periodo"] = (
            "Este bloco representa a coorte de produção do período. "
            "Faturamento por competência e recebimentos usam suas próprias datas de referência."
        )
        return row

    return _cached("financeiro_v6", data_inicio, data_fim, load, 300)


def get_financeiro_mensal(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)
    return _cached(
        "financeiro_mensal_v6",
        data_inicio,
        data_fim,
        lambda: _all("production_financial_monthly", b),
        300,
    )


def _parse_setores(setores):
    if setores is None or not str(setores).strip():
        return []
    ids = []
    for raw in str(setores).split(","):
        raw = raw.strip()
        if not raw:
            continue
        if not raw.isdigit() or int(raw) <= 0:
            raise ValueError("Setores devem ser códigos inteiros positivos separados por vírgula.")
        value = int(raw)
        if value not in ids:
            ids.append(value)
    if len(ids) > 30:
        raise ValueError("Informe no máximo 30 setores por consulta.")
    return ids


def _dataset_params(data_inicio, data_fim, setores=None):
    b = binds(data_inicio, data_fim)
    b["setores"] = _parse_setores(setores)
    return b


def _sector_cached(name, data_inicio, data_fim, setores, loader, ttl=180):
    setor_ids = _parse_setores(setores)
    setor_key = ",".join(map(str, setor_ids)) or "TODOS"
    key = (name, data_inicio.isoformat(), data_fim.isoformat(), setor_key)
    return get_or_set_cache(key, ttl, loader)


def get_faturamento_competencia_resumo(data_inicio: date, data_fim: date, setores=None):
    params = _dataset_params(data_inicio, data_fim, setores)

    def load():
        row = _one("billing_competence_summary", params) or {}
        row["semantica_periodo"] = "Período aplicado à competência de faturamento."
        row["setores_aplicados"] = params["setores"]
        row.setdefault(
            "regra_competencia",
            "A regra operacional de composição é fornecida pelo adapter privado.",
        )
        return row

    return _sector_cached("billing_competence_summary_v1", data_inicio, data_fim, setores, load, 300)


def get_faturamento_competencia_mensal(data_inicio: date, data_fim: date, setores=None):
    params = _dataset_params(data_inicio, data_fim, setores)
    return _sector_cached(
        "billing_competence_monthly_v1",
        data_inicio,
        data_fim,
        setores,
        lambda: _all("billing_competence_monthly", params),
        180,
    )


def get_faturamento_competencia_setores(data_inicio: date, data_fim: date, setores=None):
    params = _dataset_params(data_inicio, data_fim, setores)
    return _sector_cached(
        "billing_competence_sectors_v1",
        data_inicio,
        data_fim,
        setores,
        lambda: _all("billing_competence_sectors", params),
        180,
    )


def get_resumo_integrado(data_inicio: date, data_fim: date, setores=None):
    setor_ids = _parse_setores(setores)
    setor_text = ",".join(map(str, setor_ids))
    key = ("resumo_integrado_v6", data_inicio.isoformat(), data_fim.isoformat(), setor_text or "TODOS")
    hit = get_cache(key, 90)
    if hit is not None:
        return hit

    producao = get_financeiro(data_inicio, data_fim) or {}
    faturamento = get_faturamento_competencia_resumo(data_inicio, data_fim, setor_text) or {}
    recebimentos = get_pagamentos_resumo(data_inicio, data_fim) or {}
    auditoria_receb = get_auditoria_recebimentos_resumo(data_inicio, data_fim) or {}
    auditoria_prod = get_auditoria_resumo(data_inicio, data_fim) or {}

    alertas = []
    if int(auditoria_prod.get("qt_sem_nota") or 0) > 0:
        alertas.append({"nivel": "atencao", "tipo": "SEM_NOTA", "quantidade": int(auditoria_prod.get("qt_sem_nota") or 0), "texto": "Contas da produção sem documento de faturamento."})
    if int(auditoria_prod.get("qt_remessa_paga_sem_recebimento") or 0) > 0:
        alertas.append({"nivel": "critico", "tipo": "LOTE_PAGO_SEM_RECEBIMENTO", "quantidade": int(auditoria_prod.get("qt_remessa_paga_sem_recebimento") or 0), "texto": "Lotes marcados como pagos sem evento financeiro identificado."})
    if int(auditoria_prod.get("qt_receb_maior_faturado") or 0) > 0:
        alertas.append({"nivel": "critico", "tipo": "RECEBIDO_MAIOR_FATURADO", "quantidade": int(auditoria_prod.get("qt_receb_maior_faturado") or 0), "texto": "Contas com recebimento superior ao faturado."})
    if _safe_float(auditoria_receb.get("vl_saldo_financeiro_aberto")) > 0.01:
        alertas.append({"nivel": "atencao", "tipo": "SALDO_FINANCEIRO_ABERTO", "valor": _safe_float(auditoria_receb.get("vl_saldo_financeiro_aberto")), "texto": "Há saldo financeiro aberto nas contas recebidas no período."})
    if _safe_float(auditoria_receb.get("vl_saldo_glosado")) > 0.01:
        alertas.append({"nivel": "atencao", "tipo": "SALDO_AJUSTADO", "valor": _safe_float(auditoria_receb.get("vl_saldo_glosado")), "texto": "Há saldo associado a ajustes nas contas recebidas no período."})

    value = {
        "versao_modelo": "6.0-public-contract",
        "periodo": {"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()},
        "setores": setor_ids,
        "escopos": [
            {"id": "producao", "titulo": "Produção", "campo_data": "production_date", "explicacao": "O que foi produzido no período."},
            {"id": "faturamento_competencia", "titulo": "Faturamento por competência", "campo_data": "competence_date", "explicacao": "O que entrou no ciclo de faturamento por competência."},
            {"id": "recebimentos", "titulo": "Recebimentos", "campo_data": "receipt_date", "explicacao": "O que o financeiro registrou como recebido no período; pode pertencer a competências anteriores."},
        ],
        "producao": {
            "valor_contas": _safe_float(producao.get("vl_faturado")),
            "valor_remetido": _safe_float(producao.get("vl_remetido")),
            "valor_nao_remetido": _safe_float(producao.get("vl_nao_remetido")),
            "qt_atendimentos": int(producao.get("qt_atendimentos") or 0),
            "qt_contas": int(producao.get("qt_contas") or 0),
            "qt_remessas": int(producao.get("qt_remessas") or 0),
        },
        "faturamento_competencia": {
            "valor": _safe_float(faturamento.get("vl_faturamento_competencia")),
            "ambulatorial": _safe_float(faturamento.get("vl_ambulatorial")),
            "hospitalar": _safe_float(faturamento.get("vl_hospitalar")),
            "qt_itens": int(faturamento.get("qt_itens") or 0),
            "qt_contas": int(faturamento.get("qt_contas") or 0),
            "qt_atendimentos": int(faturamento.get("qt_atendimentos") or 0),
            "qt_remessas": int(faturamento.get("qt_remessas") or 0),
            "regra": faturamento.get("regra_competencia"),
        },
        "recebimentos": {
            "recebido_financeiro": _safe_float(recebimentos.get("vl_recebido_financeiro")),
            "recebido_base": _safe_float(recebimentos.get("vl_recebido_base")),
            "acrescimos": _safe_float(recebimentos.get("vl_acrescimo")),
            "ajustes_no_recebimento": _safe_float(recebimentos.get("vl_glosa_recebimento")),
            "qt_eventos": int(recebimentos.get("qt_eventos_recebimento") or 0),
            "qt_contas": int(recebimentos.get("qt_contas_recebidas") or 0),
            "qt_pacientes": int(recebimentos.get("qt_pacientes") or 0),
        },
        "pendencias_recebimentos": {
            "saldo_financeiro_aberto": _safe_float(auditoria_receb.get("vl_saldo_financeiro_aberto")),
            "saldo_ajustado": _safe_float(auditoria_receb.get("vl_saldo_glosado")),
            "qt_recebidas": int(auditoria_receb.get("qt_recebidas") or 0),
            "qt_recebidas_com_ajuste": int(auditoria_receb.get("qt_recebidas_com_glosa") or 0),
            "qt_parciais": int(auditoria_receb.get("qt_parcialmente_recebidas") or 0) + int(auditoria_receb.get("qt_parcialmente_recebidas_com_glosa") or 0),
        },
        "qualidade_producao": {
            "qt_sem_nota": int(auditoria_prod.get("qt_sem_nota") or 0),
            "qt_sem_recebimento": int(auditoria_prod.get("qt_sem_recebimento") or 0),
            "qt_lote_pago_sem_recebimento": int(auditoria_prod.get("qt_remessa_paga_sem_recebimento") or 0),
            "qt_receb_maior_faturado": int(auditoria_prod.get("qt_receb_maior_faturado") or 0),
        },
        "alertas": alertas,
        "nota_integracao": (
            "As métricas preservam suas datas de referência. "
            "Não subtraia diretamente faturamento por competência e recebimentos do mesmo intervalo."
        ),
        "validacao_competencia": "A implementação operacional e sua homologação pertencem ao adapter privado.",
    }
    return set_cache(key, value)


def get_glosas_motivos(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)
    return _cached("adjustment_reasons_v1", data_inicio, data_fim, lambda: _all("adjustment_reasons", b), 120)


def get_glosas(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 250))
    rows = _cached("adjustments_v1", data_inicio, data_fim, lambda: _all("adjustments", b), 120)
    return rows[:limit]


def get_produtos(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 250))
    rows = _cached("products_v1", data_inicio, data_fim, lambda: _all("products", b), 180)
    return rows[:limit]


def get_atendimentos(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    caps = _require_patient_support()
    b["include_medication_cost"] = bool(caps.get("custo_medicamento"))
    limit = max(1, min(limit, 500))
    rows = _cached("encounters_v1", data_inicio, data_fim, lambda: _all("encounters", b), 120)
    return rows[:limit]


def get_pacientes(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    caps = _require_patient_support()
    b["include_medication_cost"] = bool(caps.get("custo_medicamento"))
    limit = max(1, min(limit, 500))
    rows = _cached("patients_v1", data_inicio, data_fim, lambda: _all("patients", b), 150)
    return rows[:limit]


def get_paciente_contas(data_inicio: date, data_fim: date, cd_paciente: int):
    b = binds(data_inicio, data_fim)
    b["cd_paciente"] = int(cd_paciente)
    _require_patient_support()
    return _all("patient_accounts", b)


def get_conta_detalhe(cd_reg_amb: int):
    conta_id = int(cd_reg_amb)
    params = {"cd_reg_amb": conta_id}
    cabecalho = _one("account_header", params)
    if not cabecalho:
        raise ValueError("Conta não encontrada no adapter configurado.")
    return {
        "conta": cabecalho,
        "itens": _all("account_items", params),
        "glosas": _all("account_adjustments", params),
        "recebimentos": _all("account_receipts", params),
        "fonte_itens": "Contrato público InvoiceItem",
        "rotulo_recebimento": "Data registrada pelo evento financeiro",
    }


def get_remessas(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    _require_patient_support()
    _require_receipt_support()
    limit = max(1, min(limit, 500))
    rows = _cached("billing_batches_v1", data_inicio, data_fim, lambda: _all("billing_batches", b), 150)
    return rows[:limit]


def get_historico_competencias(data_inicio: date, data_fim: date):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)
    return _cached("receipt_history_v1", data_inicio, data_fim, lambda: _all("receipt_history", b), 300)


def get_pagamentos_resumo(data_inicio: date, data_fim: date):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)

    def load():
        row = _one("receipt_summary", b) or {}
        row["semantica_periodo"] = "Período aplicado à data do evento financeiro de recebimento."
        row["fonte"] = "ReceiptEvent + ReceiptAdjustment + InvoiceItem"
        row["rotulo_data"] = "Data registrada pelo evento financeiro"
        return row

    return _cached("receipt_summary_v1", data_inicio, data_fim, load, 300)


def get_pagamentos_competencia(data_inicio: date, data_fim: date):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)
    return _cached("receipt_by_competence_v1", data_inicio, data_fim, lambda: _all("receipt_by_competence", b), 300)


def get_pagamentos_eventos(data_inicio: date, data_fim: date, limit: int = 100):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 500))
    rows = _cached("receipt_events_v1", data_inicio, data_fim, lambda: _all("receipt_events", b), 120)
    return rows[:limit]


def get_pagamentos_contas(data_inicio: date, data_fim: date, limit: int = 100):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 500))
    rows = _cached("receipt_accounts_v1", data_inicio, data_fim, lambda: _all("receipt_accounts", b), 150)
    return rows[:limit]


def get_pagamentos_aging(data_inicio: date, data_fim: date):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)
    return _cached("receipt_aging_v1", data_inicio, data_fim, lambda: _one("receipt_aging", b) or {}, 300)


def get_pagamento_itens(cd_reccon_rec: int, limit: int = 500):
    _require_receipt_support()
    limit = max(1, min(limit, 1000))
    key = ("receipt_event_items_v1", int(cd_reccon_rec))
    hit = get_cache(key, 180)
    if hit is not None:
        return hit[:limit]
    rows = _all("receipt_event_items", {"cd_reccon_rec": int(cd_reccon_rec)})
    set_cache(key, rows)
    return rows[:limit]


def get_auditoria_resumo(data_inicio: date, data_fim: date):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)

    def load():
        row = _one("production_audit_summary", b) or {}
        row["tipo_auditoria"] = "PRODUCAO"
        row["semantica_periodo"] = (
            "Período aplicado à produção; recebimentos são acumulados segundo o contrato do adapter."
        )
        return row

    return _cached("production_audit_summary_v1", data_inicio, data_fim, load, 180)


def get_auditoria_detalhe(data_inicio: date, data_fim: date, limit: int = 200):
    _require_receipt_support()
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 500))
    rows = _cached("production_audit_detail_v1", data_inicio, data_fim, lambda: _all("production_audit_detail", b), 180)
    return rows[:limit]


def get_auditoria_recebimentos_resumo(data_inicio: date, data_fim: date):
    rows = get_pagamentos_contas(data_inicio, data_fim, 500)

    def sv(k):
        return sum(_safe_float(r.get(k)) for r in rows)

    statuses = {}
    for r in rows:
        st = r.get("status_recebimento") or "SEM_STATUS"
        statuses[st] = statuses.get(st, 0) + 1

    return {
        "tipo_auditoria": "RECEBIMENTOS",
        "semantica_periodo": "Período aplicado à data do evento financeiro de recebimento.",
        "qt_contas": len(rows),
        "qt_recebidas": statuses.get("RECEBIDA", 0),
        "qt_recebidas_com_glosa": statuses.get("RECEBIDA_COM_GLOSA", 0),
        "qt_parcialmente_recebidas": statuses.get("PARCIALMENTE_RECEBIDA", 0),
        "qt_parcialmente_recebidas_com_glosa": statuses.get("PARCIALMENTE_RECEBIDA_COM_GLOSA", 0),
        "qt_multiplos_recebimentos": sum(1 for r in rows if int(r.get("qt_eventos_acumulados") or 0) > 1),
        "vl_faturado": round(sv("vl_faturado"), 2),
        "vl_recebido_base_periodo": round(sv("vl_recebido_base_periodo"), 2),
        "vl_glosa_periodo": round(sv("vl_glosa_periodo"), 2),
        "vl_saldo_total_estimado": round(sv("vl_saldo_estimado"), 2),
        "vl_saldo_glosado": round(sv("vl_saldo_glosado"), 2),
        "vl_saldo_financeiro_aberto": round(sv("vl_saldo_financeiro_aberto"), 2),
        "truncado": len(rows) >= 500,
    }


def get_auditoria_recebimentos_detalhe(data_inicio: date, data_fim: date, limit: int = 200):
    rows = get_pagamentos_contas(data_inicio, data_fim, min(max(limit, 1), 500))
    return [r for r in rows if r.get("status_recebimento") != "RECEBIDA"]


def get_comparativo(data_inicio: date, data_fim: date):
    binds(data_inicio, data_fim)
    dias = (data_fim - data_inicio).days + 1
    prev_fim = data_inicio - timedelta(days=1)
    prev_inicio = prev_fim - timedelta(days=dias - 1)

    atual_fin = get_financeiro(data_inicio, data_fim) or {}
    anterior_fin = get_financeiro(prev_inicio, prev_fim) or {}
    atual_rec = get_pagamentos_resumo(data_inicio, data_fim) or {}
    anterior_rec = get_pagamentos_resumo(prev_inicio, prev_fim) or {}

    metricas = []
    specs = [
        ("Faturado", "vl_faturado", atual_fin, anterior_fin),
        ("Remetido", "vl_remetido", atual_fin, anterior_fin),
        ("Glosa líquida", "vl_glosa_liquida", atual_fin, anterior_fin),
        ("Recebimento financeiro", "vl_recebido_financeiro", atual_rec, anterior_rec),
        ("Recebimento base", "vl_recebido_base", atual_rec, anterior_rec),
        ("Contas recebidas", "qt_contas_recebidas", atual_rec, anterior_rec),
    ]
    for label, key, cur, prev in specs:
        metricas.append({
            "indicador": label,
            "atual": cur.get(key) or 0,
            "anterior": prev.get(key) or 0,
            "variacao_pct": _delta_pct(cur.get(key), prev.get(key)),
        })

    return {
        "periodo_atual": {"inicio": data_inicio, "fim": data_fim},
        "periodo_anterior": {"inicio": prev_inicio, "fim": prev_fim},
        "metricas": metricas,
        "nota": "Produção, competência e recebimento mantêm semânticas temporais independentes.",
    }
