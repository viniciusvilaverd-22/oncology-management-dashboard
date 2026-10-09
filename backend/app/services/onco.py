from datetime import date, timedelta
from app.db.oracle import fetch_all, fetch_one
from app.queries.resumo import RESUMO
from app.queries.financeiro import FINANCEIRO_RESUMO, FINANCEIRO_MENSAL
from app.queries.faturamento_competencia import (
    FATURAMENTO_COMPETENCIA_RESUMO,
    FATURAMENTO_COMPETENCIA_MENSAL,
    FATURAMENTO_COMPETENCIA_SETORES,
)
from app.queries.glosas import GLOSAS_MOTIVOS, GLOSAS_DETALHE
from app.queries.produtos import PRODUTOS
from app.queries.schema import SCHEMA_CAPABILITIES
from app.queries.detalhes import (
    ATENDIMENTOS_DETALHE,
    ATENDIMENTOS_DETALHE_COM_CUSTO,
    PACIENTES_RESUMO,
    PACIENTES_RESUMO_COM_CUSTO,
    REMESSAS_RESUMO,
    PACIENTE_CONTAS,
    CONTA_CABECALHO,
    CONTA_ITENS,
    CONTA_GLOSAS,
    CONTA_RECEBIMENTOS,
)
from app.queries.pagamentos import (
    PAGAMENTOS_RESUMO,
    PAGAMENTOS_COMPETENCIA,
    PAGAMENTOS_EVENTOS,
    PAGAMENTOS_CONTAS,
    PAGAMENTOS_AGING,
    PAGAMENTO_ITENS_EVENTO,
    HISTORICO_COMPETENCIAS,
)
from app.queries.auditoria import AUDITORIA_RESUMO, AUDITORIA_DETALHE
from app.services.cache import get_cache, set_cache, get_or_set_cache

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


def get_schema_capabilities():
    key = ("schema_capabilities_v5",)
    hit = get_cache(key, 3600)
    if hit is not None:
        return hit
    row = fetch_one(SCHEMA_CAPABILITIES, {}) or {}
    patient_ok = all(int(row.get(k) or 0) > 0 for k in (
        "atendime_cd_atendimento", "atendime_cd_paciente",
        "paciente_cd_paciente", "paciente_nm_paciente",
    ))
    cost_ok = all(int(row.get(k) or 0) > 0 for k in (
        "custo_cd_atendimento", "custo_vl_medicamento",
    ))
    receipt_ok = all(int(row.get(k) or 0) > 0 for k in (
        "rec_cd_reccon_rec", "rec_dt_recebimento", "rec_dt_estorno",
        "aj_cd_itfat_nf", "aj_cd_reccon_rec", "aj_vl_recebido", "aj_vl_acrescimo",
        "nf_cd_reg_amb", "nf_cd_remessa", "fncp_cd_itfat_nf", "fncp_dt_competencia", "fncp_vl_faturado",
    ))
    value = {
        "pacientes": patient_ok,
        "custo_medicamento": cost_ok,
        "recebimento_efetivo": receipt_ok,
        "fonte_recebimento": (
            "RECCON_REC.DT_RECEBIMENTO + V_AJUSTES_RECEBIMENTO_DET, "
            "com V_FNCP_ITEM_CONVENIO e ITFAT_NOTA_FISCAL para rastreabilidade."
            if receipt_ok else "Estrutura de recebimento validada não disponível neste schema."
        ),
        "semantica_recebimento": (
            "Data de recebimento registrada no financeiro; não é rotulada como data bancária."
        ),
        "periodo_maximo_dias": MAX_DAYS,
    }
    return set_cache(key, value)


def _require_patient_schema():
    caps = get_schema_capabilities()
    if not caps.get("pacientes"):
        raise ValueError(
            "Estrutura de paciente não validada neste banco: esperado ATENDIME.CD_PACIENTE "
            "e PACIENTE(CD_PACIENTE, NM_PACIENTE)."
        )
    return caps


def _require_receipt_schema():
    caps = get_schema_capabilities()
    if not caps.get("recebimento_efetivo"):
        raise ValueError("Estrutura de recebimento financeiro validada não está disponível neste banco.")
    return caps


def get_resumo(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)
    return _cached("resumo_v5", data_inicio, data_fim, lambda: fetch_one(RESUMO, b), 300)


def get_financeiro(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)

    def load():
        row = fetch_one(FINANCEIRO_RESUMO, b) or {}
        faturado = _safe_float(row.get("vl_faturado"))
        remetido = _safe_float(row.get("vl_remetido"))
        glosa_bruta = _safe_float(row.get("vl_glosa_bruta"))
        glosa_liquida = _safe_float(row.get("vl_glosa_liquida"))
        row["pct_remetido_faturado"] = round((remetido / faturado * 100), 2) if faturado else 0
        row["pct_glosa_bruta_remetido"] = round((glosa_bruta / remetido * 100), 4) if remetido else 0
        row["pct_glosa_liquida_remetido"] = round((glosa_liquida / remetido * 100), 4) if remetido else 0
        row["nota_pagamento"] = (
            "VL_REMESSAS_PAGAS continua representando apenas contas em remessas com SN_PAGA='S'. "
            "Recebimentos reais são exibidos separadamente usando RECCON_REC.DT_RECEBIMENTO."
        )
        row["semantica_periodo"] = (
            "Este bloco representa a coorte de produção oncológica CONVENIO_DEMO por ITREG_AMB.DT_PRODUCAO e valor total da conta. "
            "Não equivale ao faturamento por competência do relatório nativo; use a aba Faturamento MV para essa conciliação. "
            "A aba Pagamentos aplica o intervalo à data de recebimento financeiro."
        )
        return row

    return _cached("financeiro_v5", data_inicio, data_fim, load, 300)


def get_financeiro_mensal(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)
    return _cached("financeiro_mensal_v5", data_inicio, data_fim, lambda: fetch_all(FINANCEIRO_MENSAL, b), 300)



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


def _native_sql(sql, setor_ids):
    if not setor_ids:
        return sql.replace("/*SETOR_FILTER_HOSP*/", "").replace("/*SETOR_FILTER_AMB*/", "")
    placeholders = ", ".join(f":setor_{i}" for i in range(len(setor_ids)))
    return (
        sql.replace(
            "/*SETOR_FILTER_HOSP*/",
            f"AND NVL(IRF.CD_SETOR_PRODUZIU, IRF.CD_SETOR) IN ({placeholders})",
        ).replace(
            "/*SETOR_FILTER_AMB*/",
            f"AND NVL(IRA.CD_SETOR_PRODUZIU, IRA.CD_SETOR) IN ({placeholders})",
        )
    )


def _native_binds(data_inicio, data_fim, setor_ids):
    b = binds(data_inicio, data_fim)
    for i, value in enumerate(setor_ids):
        b[f"setor_{i}"] = value
    return b


def _native_cached(name, data_inicio, data_fim, setor_ids, loader, ttl=180):
    setor_key = ",".join(map(str, setor_ids)) or "TODOS"
    key = (name, data_inicio.isoformat(), data_fim.isoformat(), setor_key)
    return get_or_set_cache(key, ttl, loader)


def get_faturamento_competencia_resumo(data_inicio: date, data_fim: date, setores=None):
    setor_ids = _parse_setores(setores)
    b = _native_binds(data_inicio, data_fim, setor_ids)
    sql = _native_sql(FATURAMENTO_COMPETENCIA_RESUMO, setor_ids)

    def load():
        row = fetch_one(sql, b) or {}
        row["semantica_periodo"] = "Período aplicado a FATURA.DT_COMPETENCIA, seguindo a regra estrutural do relatório nativo MV."
        row["setores_aplicados"] = setor_ids
        row["filtro_oncologia"] = "Sem filtro adicional por AGENDAMENTO_ONCOLOGICO; use os mesmos setores do relatório nativo (oncologia atual: setor 113)."
        row["regra_native"] = (
            "Empresa 1, CONVENIO_DEMO 11, remessa fechada, conta/item fechado, não pacote, "
            "não diagnóstico e pagamento não cancelado; soma item a item."
        )
        row["observacao_v_var"] = (
            "O placeholder dinâmico V_VAR do relatório original não foi reproduzido porque sua regra não foi fornecida."
        )
        return row

    return _native_cached("faturamento_competencia_resumo_v521", data_inicio, data_fim, setor_ids, load, 300)


def get_faturamento_competencia_mensal(data_inicio: date, data_fim: date, setores=None):
    setor_ids = _parse_setores(setores)
    b = _native_binds(data_inicio, data_fim, setor_ids)
    sql = _native_sql(FATURAMENTO_COMPETENCIA_MENSAL, setor_ids)
    return _native_cached(
        "faturamento_competencia_mensal_v521", data_inicio, data_fim, setor_ids,
        lambda: fetch_all(sql, b), 180
    )


def get_faturamento_competencia_setores(data_inicio: date, data_fim: date, setores=None):
    setor_ids = _parse_setores(setores)
    b = _native_binds(data_inicio, data_fim, setor_ids)
    sql = _native_sql(FATURAMENTO_COMPETENCIA_SETORES, setor_ids)
    return _native_cached(
        "faturamento_competencia_setores_v521", data_inicio, data_fim, setor_ids,
        lambda: fetch_all(sql, b), 180
    )


def get_resumo_integrado(data_inicio: date, data_fim: date, setores="113"):
    """Camada lógica única para a leitura executiva do painel.

    Importante: integra métricas validadas sem misturar suas bases temporais.
    Produção, faturamento MV e recebimento continuam com datas de referência
    distintas e isso é devolvido explicitamente ao frontend.
    """
    setor_ids = _parse_setores(setores or "113")
    if not setor_ids:
        setor_ids = [113]
    setor_text = ",".join(map(str, setor_ids))
    key = ("resumo_integrado_v53", data_inicio.isoformat(), data_fim.isoformat(), setor_text)
    hit = get_cache(key, 90)
    if hit is not None:
        return hit

    # Sequencial por segurança: evita pico de consultas concorrentes no Oracle.
    producao = get_financeiro(data_inicio, data_fim) or {}
    faturamento_mv = get_faturamento_competencia_resumo(data_inicio, data_fim, setor_text) or {}
    recebimentos = get_pagamentos_resumo(data_inicio, data_fim) or {}
    auditoria_receb = get_auditoria_recebimentos_resumo(data_inicio, data_fim) or {}
    auditoria_prod = get_auditoria_resumo(data_inicio, data_fim) or {}

    alertas = []
    if int(auditoria_prod.get("qt_sem_nota") or 0) > 0:
        alertas.append({"nivel": "atencao", "tipo": "SEM_NOTA", "quantidade": int(auditoria_prod.get("qt_sem_nota") or 0), "texto": "Contas da produção sem nota fiscal."})
    if int(auditoria_prod.get("qt_remessa_paga_sem_recebimento") or 0) > 0:
        alertas.append({"nivel": "critico", "tipo": "REMESSA_PAGA_SEM_RECEBIMENTO", "quantidade": int(auditoria_prod.get("qt_remessa_paga_sem_recebimento") or 0), "texto": "Remessas marcadas como pagas sem recebimento financeiro identificado."})
    if int(auditoria_prod.get("qt_receb_maior_faturado") or 0) > 0:
        alertas.append({"nivel": "critico", "tipo": "RECEBIDO_MAIOR_FATURADO", "quantidade": int(auditoria_prod.get("qt_receb_maior_faturado") or 0), "texto": "Contas com recebimento superior ao faturado."})
    if _safe_float(auditoria_receb.get("vl_saldo_financeiro_aberto")) > 0.01:
        alertas.append({"nivel": "atencao", "tipo": "SALDO_FINANCEIRO_ABERTO", "valor": _safe_float(auditoria_receb.get("vl_saldo_financeiro_aberto")), "texto": "Há saldo financeiro aberto nas contas recebidas no período."})
    if _safe_float(auditoria_receb.get("vl_saldo_glosado")) > 0.01:
        alertas.append({"nivel": "atencao", "tipo": "SALDO_GLOSADO", "valor": _safe_float(auditoria_receb.get("vl_saldo_glosado")), "texto": "Há saldo glosado nas contas recebidas no período."})

    value = {
        "versao_modelo": "5.3",
        "periodo": {"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()},
        "setores_mv": setor_ids,
        "escopos": [
            {"id": "producao", "titulo": "Produção", "campo_data": "ITREG_AMB.DT_PRODUCAO", "explicacao": "O que foi produzido pela oncologia no período."},
            {"id": "faturamento_mv", "titulo": "Faturamento MV", "campo_data": "FATURA.DT_COMPETENCIA", "explicacao": "O que entrou no faturamento oficial por competência, seguindo a regra do relatório nativo."},
            {"id": "recebimentos", "titulo": "Recebimentos", "campo_data": "RECCON_REC.DT_RECEBIMENTO", "explicacao": "O que o financeiro registrou como recebido no período; pode pertencer a competências anteriores."},
        ],
        "producao": {
            "valor_contas": _safe_float(producao.get("vl_faturado")),
            "valor_remetido": _safe_float(producao.get("vl_remetido")),
            "valor_nao_remetido": _safe_float(producao.get("vl_nao_remetido")),
            "qt_atendimentos": int(producao.get("qt_atendimentos") or 0),
            "qt_contas": int(producao.get("qt_contas") or 0),
            "qt_remessas": int(producao.get("qt_remessas") or 0),
        },
        "faturamento_mv": {
            "valor": _safe_float(faturamento_mv.get("vl_faturamento_competencia")),
            "ambulatorial": _safe_float(faturamento_mv.get("vl_ambulatorial")),
            "hospitalar": _safe_float(faturamento_mv.get("vl_hospitalar")),
            "qt_itens": int(faturamento_mv.get("qt_itens") or 0),
            "qt_contas": int(faturamento_mv.get("qt_contas") or 0),
            "qt_atendimentos": int(faturamento_mv.get("qt_atendimentos") or 0),
            "qt_remessas": int(faturamento_mv.get("qt_remessas") or 0),
            "regra": faturamento_mv.get("regra_native"),
        },
        "recebimentos": {
            "recebido_financeiro": _safe_float(recebimentos.get("vl_recebido_financeiro")),
            "recebido_base": _safe_float(recebimentos.get("vl_recebido_base")),
            "acrescimos": _safe_float(recebimentos.get("vl_acrescimo")),
            "glosa_no_recebimento": _safe_float(recebimentos.get("vl_glosa_recebimento")),
            "qt_eventos": int(recebimentos.get("qt_eventos_recebimento") or 0),
            "qt_contas": int(recebimentos.get("qt_contas_recebidas") or 0),
            "qt_pacientes": int(recebimentos.get("qt_pacientes") or 0),
        },
        "pendencias_recebimentos": {
            "saldo_financeiro_aberto": _safe_float(auditoria_receb.get("vl_saldo_financeiro_aberto")),
            "saldo_glosado": _safe_float(auditoria_receb.get("vl_saldo_glosado")),
            "qt_recebidas": int(auditoria_receb.get("qt_recebidas") or 0),
            "qt_recebidas_com_glosa": int(auditoria_receb.get("qt_recebidas_com_glosa") or 0),
            "qt_parciais": int(auditoria_receb.get("qt_parcialmente_recebidas") or 0) + int(auditoria_receb.get("qt_parcialmente_recebidas_com_glosa") or 0),
        },
        "qualidade_producao": {
            "qt_sem_nota": int(auditoria_prod.get("qt_sem_nota") or 0),
            "qt_sem_recebimento": int(auditoria_prod.get("qt_sem_recebimento") or 0),
            "qt_remessa_paga_sem_recebimento": int(auditoria_prod.get("qt_remessa_paga_sem_recebimento") or 0),
            "qt_receb_maior_faturado": int(auditoria_prod.get("qt_receb_maior_faturado") or 0),
        },
        "alertas": alertas,
        "nota_integracao": (
            "As métricas estão integradas na mesma leitura executiva, mas preservam suas datas de referência. "
            "Não subtraia diretamente faturamento MV por competência e recebimentos do mesmo intervalo: "
            "o recebimento pode corresponder a competências anteriores."
        ),
        "validacao_mv": "Metodologia do faturamento MV conciliada em homologação com o relatório nativo para o setor 113.",
    }
    return set_cache(key, value)

def get_glosas_motivos(data_inicio: date, data_fim: date):
    b = binds(data_inicio, data_fim)
    return _cached("glosas_motivos_v5", data_inicio, data_fim, lambda: fetch_all(GLOSAS_MOTIVOS, b), 120)


def get_glosas(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 250))
    rows = _cached("glosas_v5", data_inicio, data_fim, lambda: fetch_all(GLOSAS_DETALHE, b), 120)
    return rows[:limit]


def get_produtos(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 250))
    rows = _cached("produtos_v5", data_inicio, data_fim, lambda: fetch_all(PRODUTOS, b), 180)
    return rows[:limit]


def get_atendimentos(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    caps = _require_patient_schema()
    limit = max(1, min(limit, 500))
    sql = ATENDIMENTOS_DETALHE_COM_CUSTO if caps.get("custo_medicamento") else ATENDIMENTOS_DETALHE
    rows = _cached("atendimentos_v5", data_inicio, data_fim, lambda: fetch_all(sql, b), 120)
    return rows[:limit]


def get_pacientes(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    caps = _require_patient_schema()
    limit = max(1, min(limit, 500))
    sql = PACIENTES_RESUMO_COM_CUSTO if caps.get("custo_medicamento") else PACIENTES_RESUMO
    rows = _cached("pacientes_v5", data_inicio, data_fim, lambda: fetch_all(sql, b), 150)
    return rows[:limit]



def get_paciente_contas(data_inicio: date, data_fim: date, cd_paciente: int):
    b = binds(data_inicio, data_fim)
    b["cd_paciente"] = int(cd_paciente)
    _require_patient_schema()
    rows = fetch_all(PACIENTE_CONTAS, b)
    return rows


def get_conta_detalhe(cd_reg_amb: int):
    conta_id = int(cd_reg_amb)
    binds_conta = {"cd_reg_amb": conta_id}
    cabecalho = fetch_one(CONTA_CABECALHO, binds_conta)
    if not cabecalho:
        raise ValueError("Conta oncológica não encontrada para o convênio homologado.")
    itens = fetch_all(CONTA_ITENS, binds_conta)
    glosas = fetch_all(CONTA_GLOSAS, binds_conta)
    recebimentos = fetch_all(CONTA_RECEBIMENTOS, binds_conta)
    return {
        "conta": cabecalho,
        "itens": itens,
        "glosas": glosas,
        "recebimentos": recebimentos,
        "fonte_itens": "ITREG_AMB + PRO_FAT",
        "rotulo_recebimento": "Data de recebimento registrada no financeiro",
    }

def get_remessas(data_inicio: date, data_fim: date, limit: int = 100):
    b = binds(data_inicio, data_fim)
    _require_patient_schema()
    _require_receipt_schema()
    limit = max(1, min(limit, 500))
    rows = _cached("remessas_v5", data_inicio, data_fim, lambda: fetch_all(REMESSAS_RESUMO, b), 150)
    return rows[:limit]


def get_historico_competencias(data_inicio: date, data_fim: date):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)
    return _cached(
        "historico_competencias_v1",
        data_inicio,
        data_fim,
        lambda: fetch_all(HISTORICO_COMPETENCIAS, b),
        300,
    )


def get_pagamentos_resumo(data_inicio: date, data_fim: date):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)

    def load():
        row = fetch_one(PAGAMENTOS_RESUMO, b) or {}
        row["semantica_periodo"] = "Período aplicado a RECCON_REC.DT_RECEBIMENTO."
        row["fonte"] = "RECCON_REC + V_AJUSTES_RECEBIMENTO_DET + V_FNCP_ITEM_CONVENIO + ITFAT_NOTA_FISCAL"
        row["rotulo_data"] = "Data de recebimento registrada no financeiro"
        return row

    return _cached("pagamentos_resumo_v5", data_inicio, data_fim, load, 300)


def get_pagamentos_competencia(data_inicio: date, data_fim: date):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)
    return _cached("pagamentos_competencia_v5", data_inicio, data_fim, lambda: fetch_all(PAGAMENTOS_COMPETENCIA, b), 300)


def get_pagamentos_eventos(data_inicio: date, data_fim: date, limit: int = 100):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 500))
    rows = _cached("pagamentos_eventos_v5", data_inicio, data_fim, lambda: fetch_all(PAGAMENTOS_EVENTOS, b), 120)
    return rows[:limit]


def get_pagamentos_contas(data_inicio: date, data_fim: date, limit: int = 100):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 500))
    rows = _cached("pagamentos_contas_v5_1", data_inicio, data_fim, lambda: fetch_all(PAGAMENTOS_CONTAS, b), 150)
    return rows[:limit]


def get_pagamentos_aging(data_inicio: date, data_fim: date):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)
    return _cached("pagamentos_aging_v5", data_inicio, data_fim, lambda: fetch_one(PAGAMENTOS_AGING, b) or {}, 300)


def get_pagamento_itens(cd_reccon_rec: int, limit: int = 500):
    _require_receipt_schema()
    limit = max(1, min(limit, 1000))
    key = ("pagamento_itens_v5", int(cd_reccon_rec))
    hit = get_cache(key, 180)
    if hit is not None:
        return hit[:limit]
    rows = fetch_all(PAGAMENTO_ITENS_EVENTO, {"cd_reccon_rec": int(cd_reccon_rec)})
    set_cache(key, rows)
    return rows[:limit]


def get_auditoria_resumo(data_inicio: date, data_fim: date):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)

    def load():
        row = fetch_one(AUDITORIA_RESUMO, b) or {}
        row["tipo_auditoria"] = "PRODUCAO"
        row["semantica_periodo"] = (
            "Período aplicado à produção oncológica CONVENIO_DEMO. O recebimento é pesquisado de forma acumulada "
            "para as contas produzidas nesse coorte; portanto, não representa os recebimentos ocorridos no mesmo intervalo."
        )
        return row

    return _cached("auditoria_resumo_v5_1", data_inicio, data_fim, load, 180)


def get_auditoria_detalhe(data_inicio: date, data_fim: date, limit: int = 200):
    _require_receipt_schema()
    b = binds(data_inicio, data_fim)
    limit = max(1, min(limit, 500))
    rows = _cached("auditoria_detalhe_v5_1", data_inicio, data_fim, lambda: fetch_all(AUDITORIA_DETALHE, b), 180)
    return rows[:limit]


def get_auditoria_recebimentos_resumo(data_inicio: date, data_fim: date):
    """Audita apenas as contas com recebimento registrado no intervalo financeiro.

    Reutiliza a consulta de contas recebidas, cuja janela é RECCON_REC.DT_RECEBIMENTO.
    O universo oncológico é pequeno e o limite de 500 é superior ao volume esperado em 93 dias;
    o campo `truncado` deixa essa premissa visível se um dia o volume atingir o teto.
    """
    rows = get_pagamentos_contas(data_inicio, data_fim, 500)
    def sv(k):
        return sum(_safe_float(r.get(k)) for r in rows)
    statuses = {}
    for r in rows:
        st = r.get("status_recebimento") or "SEM_STATUS"
        statuses[st] = statuses.get(st, 0) + 1
    return {
        "tipo_auditoria": "RECEBIMENTOS",
        "semantica_periodo": "Período aplicado a RECCON_REC.DT_RECEBIMENTO.",
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
        "nota": "Faturamento usa coorte de produção; recebimento usa DT_RECEBIMENTO. Compare cada indicador dentro da sua própria semântica temporal.",
    }
