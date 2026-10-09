from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from app.services.onco import (
    get_resumo,
    get_resumo_integrado,
    get_financeiro,
    get_financeiro_mensal,
    get_faturamento_competencia_resumo,
    get_faturamento_competencia_mensal,
    get_faturamento_competencia_setores,
    get_glosas,
    get_glosas_motivos,
    get_produtos,
    get_atendimentos,
    get_pacientes,
    get_remessas,
    get_paciente_contas,
    get_conta_detalhe,
    get_schema_capabilities,
    get_pagamentos_resumo,
    get_pagamentos_competencia,
    get_pagamentos_eventos,
    get_pagamentos_contas,
    get_pagamentos_aging,
    get_pagamento_itens,
    get_historico_competencias,
    get_auditoria_resumo,
    get_auditoria_detalhe,
    get_auditoria_recebimentos_resumo,
    get_auditoria_recebimentos_detalhe,
    get_comparativo,
)
from app.exports.xml_export import build_xml
from app.exports.pdf_export import build_pdf, build_account_pdf
from app.exports.csv_export import build_csv
from app.auth.deps import require_user, require_onco_model, require_operational

router = APIRouter(prefix="/api/onco", tags=["Oncologia"], dependencies=[Depends(require_user), Depends(require_onco_model)])


def _guard(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/capabilities")
def capabilities():
    return _guard(get_schema_capabilities)


@router.get("/resumo")
def resumo(data_inicio: date, data_fim: date):
    return _guard(get_resumo, data_inicio, data_fim)

@router.get("/resumo-integrado")
def resumo_integrado(
    data_inicio: date,
    data_fim: date,
    setores: str | None = Query("113", max_length=200),
):
    return _guard(get_resumo_integrado, data_inicio, data_fim, setores or "113")


@router.get("/financeiro")
def financeiro(data_inicio: date, data_fim: date):
    return _guard(get_financeiro, data_inicio, data_fim)


@router.get("/financeiro/mensal")
def financeiro_mensal(data_inicio: date, data_fim: date):
    return _guard(get_financeiro_mensal, data_inicio, data_fim)

@router.get("/faturamento-competencia/resumo")
def faturamento_competencia_resumo(
    data_inicio: date,
    data_fim: date,
    setores: str | None = Query(None, max_length=200),
):
    return _guard(get_faturamento_competencia_resumo, data_inicio, data_fim, setores)


@router.get("/faturamento-competencia/mensal")
def faturamento_competencia_mensal(
    data_inicio: date,
    data_fim: date,
    setores: str | None = Query(None, max_length=200),
):
    return _guard(get_faturamento_competencia_mensal, data_inicio, data_fim, setores)


@router.get("/faturamento-competencia/setores")
def faturamento_competencia_setores(
    data_inicio: date,
    data_fim: date,
    setores: str | None = Query(None, max_length=200),
):
    return _guard(get_faturamento_competencia_setores, data_inicio, data_fim, setores)


@router.get("/comparativo")
def comparativo(data_inicio: date, data_fim: date):
    return _guard(get_comparativo, data_inicio, data_fim)


@router.get("/historico-competencias")
def historico_competencias(data_inicio: date, data_fim: date):
    return _guard(get_historico_competencias, data_inicio, data_fim)


@router.get("/pagamentos/resumo")
def pagamentos_resumo(data_inicio: date, data_fim: date):
    return _guard(get_pagamentos_resumo, data_inicio, data_fim)


@router.get("/pagamentos/competencia")
def pagamentos_competencia(data_inicio: date, data_fim: date):
    return _guard(get_pagamentos_competencia, data_inicio, data_fim)


@router.get("/pagamentos/eventos", dependencies=[Depends(require_operational)])
def pagamentos_eventos(data_inicio: date, data_fim: date, limit: int = Query(100, ge=1, le=500)):
    return _guard(get_pagamentos_eventos, data_inicio, data_fim, limit)


@router.get("/pagamentos/contas", dependencies=[Depends(require_operational)])
def pagamentos_contas(data_inicio: date, data_fim: date, limit: int = Query(100, ge=1, le=500)):
    return _guard(get_pagamentos_contas, data_inicio, data_fim, limit)


@router.get("/pagamentos/aging")
def pagamentos_aging(data_inicio: date, data_fim: date):
    return _guard(get_pagamentos_aging, data_inicio, data_fim)


@router.get("/pagamentos/eventos/{cd_reccon_rec}/itens", dependencies=[Depends(require_operational)])
def pagamento_itens(cd_reccon_rec: int, limit: int = Query(500, ge=1, le=1000)):
    return _guard(get_pagamento_itens, cd_reccon_rec, limit)


@router.get("/auditoria/resumo", dependencies=[Depends(require_operational)])
def auditoria_resumo(data_inicio: date, data_fim: date):
    return _guard(get_auditoria_resumo, data_inicio, data_fim)


@router.get("/auditoria/detalhe", dependencies=[Depends(require_operational)])
def auditoria_detalhe(data_inicio: date, data_fim: date, limit: int = Query(200, ge=1, le=500)):
    return _guard(get_auditoria_detalhe, data_inicio, data_fim, limit)


@router.get("/auditoria/recebimentos/resumo", dependencies=[Depends(require_operational)])
def auditoria_recebimentos_resumo(data_inicio: date, data_fim: date):
    return _guard(get_auditoria_recebimentos_resumo, data_inicio, data_fim)


@router.get("/auditoria/recebimentos/detalhe", dependencies=[Depends(require_operational)])
def auditoria_recebimentos_detalhe(data_inicio: date, data_fim: date, limit: int = Query(200, ge=1, le=500)):
    return _guard(get_auditoria_recebimentos_detalhe, data_inicio, data_fim, limit)


@router.get("/atendimentos", dependencies=[Depends(require_operational)])
def atendimentos(data_inicio: date, data_fim: date, limit: int = Query(100, ge=1, le=500)):
    return _guard(get_atendimentos, data_inicio, data_fim, limit)


@router.get("/pacientes", dependencies=[Depends(require_operational)])
def pacientes(data_inicio: date, data_fim: date, limit: int = Query(100, ge=1, le=500)):
    return _guard(get_pacientes, data_inicio, data_fim, limit)


@router.get("/remessas", dependencies=[Depends(require_operational)])
def remessas(data_inicio: date, data_fim: date, limit: int = Query(100, ge=1, le=500)):
    return _guard(get_remessas, data_inicio, data_fim, limit)


@router.get("/pacientes/{cd_paciente}/contas", dependencies=[Depends(require_operational)])
def paciente_contas(cd_paciente: int, data_inicio: date, data_fim: date):
    return _guard(get_paciente_contas, data_inicio, data_fim, cd_paciente)


@router.get("/contas/{cd_reg_amb}", dependencies=[Depends(require_operational)])
def conta_detalhe(cd_reg_amb: int):
    return _guard(get_conta_detalhe, cd_reg_amb)


@router.get("/contas/{cd_reg_amb}/pdf", dependencies=[Depends(require_operational)])
def conta_pdf(cd_reg_amb: int):
    payload = _guard(get_conta_detalhe, cd_reg_amb)
    pdf_bytes = build_account_pdf(payload)
    filename = f"conta_oncologia_{cd_reg_amb}.pdf"
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="{filename}"'})


@router.get("/glosas", dependencies=[Depends(require_operational)])
def glosas(data_inicio: date, data_fim: date, limit: int = Query(100, ge=1, le=250)):
    return _guard(get_glosas, data_inicio, data_fim, limit)


@router.get("/glosas/motivos", dependencies=[Depends(require_operational)])
def glosas_motivos(data_inicio: date, data_fim: date):
    return _guard(get_glosas_motivos, data_inicio, data_fim)


@router.get("/produtos", dependencies=[Depends(require_operational)])
def produtos(data_inicio: date, data_fim: date, limit: int = Query(100, ge=1, le=250)):
    return _guard(get_produtos, data_inicio, data_fim, limit)


@router.get("/export/pdf", dependencies=[Depends(require_operational)])
def export_pdf(data_inicio: date, data_fim: date, detalhado: bool = Query(False)):
    # Exportação explícita e sequencial para evitar pico de carga no Oracle.
    resumo_data = _guard(get_resumo, data_inicio, data_fim)
    financeiro_data = _guard(get_financeiro, data_inicio, data_fim)
    mensal_data = _guard(get_financeiro_mensal, data_inicio, data_fim)
    motivos_data = _guard(get_glosas_motivos, data_inicio, data_fim)
    glosas_data = _guard(get_glosas, data_inicio, data_fim, 100)
    produtos_data = _guard(get_produtos, data_inicio, data_fim, 100)
    pagamentos_data = _guard(get_pagamentos_resumo, data_inicio, data_fim)
    pagamentos_comp_data = _guard(get_pagamentos_competencia, data_inicio, data_fim)

    atendimentos_data = []
    pacientes_data = []
    remessas_data = []
    eventos_data = []
    auditoria_data = {}
    if detalhado:
        atendimentos_data = _guard(get_atendimentos, data_inicio, data_fim, 200)
        pacientes_data = _guard(get_pacientes, data_inicio, data_fim, 150)
        remessas_data = _guard(get_remessas, data_inicio, data_fim, 150)
        eventos_data = _guard(get_pagamentos_eventos, data_inicio, data_fim, 150)
        auditoria_data = _guard(get_auditoria_resumo, data_inicio, data_fim)

    pdf_bytes = build_pdf(
        data_inicio.isoformat(),
        data_fim.isoformat(),
        resumo_data or {},
        financeiro_data or {},
        mensal_data or [],
        motivos_data or [],
        glosas_data or [],
        produtos_data or [],
        atendimentos=atendimentos_data,
        pacientes=pacientes_data,
        remessas=remessas_data,
        pagamentos=pagamentos_data or {},
        pagamentos_competencia=pagamentos_comp_data or [],
        pagamentos_eventos=eventos_data,
        auditoria=auditoria_data or {},
        detalhado=detalhado,
    )

    suffix = "_detalhado" if detalhado else ""
    filename = f"relatorio_oncologia_{data_inicio}_{data_fim}{suffix}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/xml", dependencies=[Depends(require_operational)])
def export_xml(data_inicio: date, data_fim: date):
    resumo_data = _guard(get_resumo, data_inicio, data_fim)
    financeiro_data = _guard(get_financeiro, data_inicio, data_fim)
    glosas_data = _guard(get_glosas, data_inicio, data_fim, 100)
    produtos_data = _guard(get_produtos, data_inicio, data_fim, 100)

    xml_bytes = build_xml(
        data_inicio.isoformat(), data_fim.isoformat(), resumo_data, financeiro_data, glosas_data, produtos_data
    )
    filename = f"oncologia_{data_inicio}_{data_fim}.xml"
    return Response(content=xml_bytes, media_type="application/xml", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/export/pagamentos.csv", dependencies=[Depends(require_operational)])
def export_pagamentos_csv(data_inicio: date, data_fim: date):
    rows = _guard(get_pagamentos_contas, data_inicio, data_fim, 500)
    columns = [
        ("nm_paciente", "Paciente"), ("cd_atendimento", "Atendimento"), ("cd_reg_amb", "Conta"),
        ("cd_remessa", "Remessa"), ("dt_competencia", "Competencia"), ("dt_atendimento", "Data atendimento"),
        ("primeiro_recebimento_no_periodo", "Primeiro recebimento no periodo"),
        ("ultimo_recebimento_no_periodo", "Ultimo recebimento no periodo"),
        ("vl_faturado", "Valor faturado"), ("vl_recebido_financeiro_periodo", "Recebimento financeiro no periodo"),
        ("vl_recebido_base_periodo", "Recebimento base no periodo"), ("vl_acrescimo_periodo", "Acrescimos no periodo"),
        ("vl_recebido_base_acum", "Recebimento base acumulado"), ("vl_glosa_acum", "Glosa acumulada"),
        ("vl_saldo_estimado", "Saldo total estimado"), ("vl_saldo_glosado", "Saldo glosado"),
        ("vl_saldo_financeiro_aberto", "Saldo financeiro aberto"), ("status_recebimento", "Status recebimento"),
    ]
    content = build_csv(rows, columns)
    filename = f"pagamentos_oncologia_{data_inicio}_{data_fim}.csv"
    return Response(content=content, media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/export/faturamento-competencia.csv", dependencies=[Depends(require_operational)])
def export_faturamento_competencia_csv(
    data_inicio: date,
    data_fim: date,
    setores: str | None = Query(None, max_length=200),
):
    rows = _guard(get_faturamento_competencia_setores, data_inicio, data_fim, setores)
    columns = [
        ("cd_setor", "Codigo setor"), ("nm_setor", "Setor"),
        ("vl_faturamento_competencia", "Faturamento competencia MV"),
        ("vl_ambulatorial", "Ambulatorial"), ("vl_hospitalar", "Hospitalar"),
        ("qt_itens", "Itens"), ("qt_contas", "Contas"),
        ("qt_atendimentos", "Atendimentos"), ("qt_remessas", "Remessas"),
    ]
    content = build_csv(rows, columns)
    filename = f"faturamento_competencia_mv_{data_inicio}_{data_fim}.csv"
    return Response(content=content, media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/export/atendimentos.csv", dependencies=[Depends(require_operational)])
def export_atendimentos_csv(data_inicio: date, data_fim: date):
    rows = _guard(get_atendimentos, data_inicio, data_fim, 500)
    columns = [
        ("nm_paciente", "Paciente"), ("cd_atendimento", "Atendimento"), ("cd_reg_amb", "Conta"),
        ("cd_remessa", "Remessa"), ("dt_atendimento", "Data atendimento"), ("vl_faturado", "Faturado"),
        ("vl_glosa_liquida", "Glosa liquida"), ("vl_recebido_base", "Recebido base acumulado"),
        ("vl_acrescimo_recebimento", "Acrescimos"), ("vl_saldo_estimado", "Saldo estimado"),
        ("status_financeiro", "Status financeiro"), ("primeiro_recebimento", "Primeiro recebimento"),
        ("ultimo_recebimento", "Ultimo recebimento"),
    ]
    content = build_csv(rows, columns)
    filename = f"atendimentos_oncologia_{data_inicio}_{data_fim}.csv"
    return Response(content=content, media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/export/pacientes.csv", dependencies=[Depends(require_operational)])
def export_pacientes_csv(data_inicio: date, data_fim: date):
    rows = _guard(get_pacientes, data_inicio, data_fim, 500)
    columns = [
        ("nm_paciente", "Paciente"), ("qt_atendimentos", "Atendimentos"), ("qt_contas", "Contas"),
        ("qt_remessas", "Remessas"), ("vl_faturado", "Faturado"), ("vl_glosa_liquida", "Glosa liquida"),
        ("vl_recebido_base", "Recebido base"), ("vl_acrescimo_recebimento", "Acrescimos"),
        ("vl_saldo_estimado", "Saldo estimado"), ("vl_medio_por_atendimento", "Media faturada por atendimento"),
        ("vl_recebido_medio_atendimento", "Media recebida por atendimento"),
    ]
    content = build_csv(rows, columns)
    filename = f"pacientes_oncologia_{data_inicio}_{data_fim}.csv"
    return Response(content=content, media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}"'})
