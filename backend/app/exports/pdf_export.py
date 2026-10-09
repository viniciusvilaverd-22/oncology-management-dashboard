from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    LongTable,
    PageBreak,
    KeepTogether,
)

PAGE_SIZE = landscape(A4)
PAGE_W, PAGE_H = PAGE_SIZE

BLACK = colors.HexColor("#171717")
DARK = colors.HexColor("#252525")
GOLD = colors.HexColor("#B69455")
GOLD_LIGHT = colors.HexColor("#F4EFE4")
CREAM = colors.HexColor("#FAF8F3")
GRAY_050 = colors.HexColor("#FAFAFA")
GRAY_100 = colors.HexColor("#F1F1F1")
GRAY_200 = colors.HexColor("#E3E3E3")
GRAY_500 = colors.HexColor("#777777")
RED_LIGHT = colors.HexColor("#F8ECEC")
RED = colors.HexColor("#9E3F3F")
GREEN_LIGHT = colors.HexColor("#EDF5ED")
GREEN = colors.HexColor("#3D6B45")


def _n(v: Any) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def brl(v: Any) -> str:
    s = f"{_n(v):,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def integer(v: Any) -> str:
    try:
        return f"{int(v or 0):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def percent(v: Any, digits: int = 2) -> str:
    try:
        return f"{float(v or 0):.{digits}f}%".replace(".", ",")
    except (TypeError, ValueError):
        return "0,00%"


def safe(v: Any, fallback: str = "-") -> str:
    if v is None:
        return fallback
    txt = str(v).strip()
    return txt or fallback


def short_date(v: Any) -> str:
    if not v:
        return "-"
    txt = str(v)
    if len(txt) >= 10:
        return txt[:10]
    return txt


styles = getSampleStyleSheet()
S_TITLE = ParagraphStyle(
    "ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=22, leading=25, textColor=BLACK, spaceAfter=2,
)
S_SUBTITLE = ParagraphStyle(
    "ReportSubtitle", parent=styles["Normal"], fontName="Helvetica",
    fontSize=9.5, leading=13, textColor=GRAY_500,
)
S_SECTION = ParagraphStyle(
    "Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=14, leading=17, textColor=BLACK, spaceBefore=3, spaceAfter=8,
)
S_BODY = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=8.5, leading=12, textColor=DARK,
)
S_SMALL = ParagraphStyle(
    "Small", parent=S_BODY, fontSize=7.2, leading=9.5, textColor=GRAY_500,
)
S_CARD_LABEL = ParagraphStyle(
    "CardLabel", parent=S_SMALL, fontName="Helvetica-Bold",
    fontSize=6.9, leading=8.2, textColor=GRAY_500,
)
S_CARD_VALUE = ParagraphStyle(
    "CardValue", parent=S_BODY, fontName="Helvetica-Bold",
    fontSize=14.5, leading=17, textColor=BLACK,
)
S_RIGHT = ParagraphStyle(
    "Right", parent=S_BODY, alignment=TA_RIGHT,
)
S_CELL = ParagraphStyle(
    "Cell", parent=S_BODY, fontSize=7.1, leading=9,
)
S_CELL_SMALL = ParagraphStyle(
    "CellSmall", parent=S_BODY, fontSize=6.4, leading=8,
)
S_HEAD = ParagraphStyle(
    "Head", parent=S_CELL, fontName="Helvetica-Bold", textColor=colors.white,
)


def P(text: Any, style=S_CELL) -> Paragraph:
    # Keep content plain and safe for Paragraph markup.
    txt = safe(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(txt, style)


def _page_header_footer(canvas, doc):
    canvas.saveState()
    # top rule + institutional label
    canvas.setFillColor(BLACK)
    canvas.rect(0, PAGE_H - 11 * mm, PAGE_W, 11 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(14 * mm, PAGE_H - 7.1 * mm, "HOSPITAL DEMONSTRATIVO  |  TI")
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H - 11.8 * mm, PAGE_W, 0.8 * mm, fill=1, stroke=0)

    canvas.setFillColor(GRAY_500)
    canvas.setFont("Helvetica", 6.8)
    canvas.drawString(14 * mm, 8 * mm, "Hospital ERP - Oncologia Convênio Demo | Relatorio gerencial")
    canvas.drawRightString(PAGE_W - 14 * mm, 8 * mm, f"Pagina {canvas.getPageNumber()}")
    canvas.setStrokeColor(GRAY_200)
    canvas.line(14 * mm, 11 * mm, PAGE_W - 14 * mm, 11 * mm)
    canvas.restoreState()




def _account_page_header_footer(canvas, doc):
    canvas.saveState()
    # Header exclusivo do detalhe de conta: fundo claro e marca institucional.
    canvas.setFillColor(colors.white)
    canvas.rect(0, PAGE_H - 16 * mm, PAGE_W, 16 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.8)
    canvas.line(0, PAGE_H - 16 * mm, PAGE_W, PAGE_H - 16 * mm)

    canvas.setFillColor(BLACK)
    canvas.setFont("Helvetica-Bold", 7.7)
    canvas.drawString(39 * mm, PAGE_H - 7.2 * mm, "HOSPITAL DEMONSTRATIVO")
    canvas.setFont("Helvetica", 6.9)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(39 * mm, PAGE_H - 11.0 * mm, "Oncologia Integrada | TI - Hospital Demonstrativo")

    canvas.setFillColor(GRAY_500)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(14 * mm, 8 * mm, "Documento interno de conferencia - nao substitui documento fiscal.")
    canvas.drawRightString(PAGE_W - 14 * mm, 8 * mm, f"Pagina {canvas.getPageNumber()}")
    canvas.setStrokeColor(GRAY_200)
    canvas.line(14 * mm, 11 * mm, PAGE_W - 14 * mm, 11 * mm)
    canvas.restoreState()


def _account_items_table(headers: list[str], rows: Iterable[Iterable[Any]], widths: list[float]) -> LongTable:
    data = [[Paragraph(h, S_HEAD) for h in headers]]
    for row in rows:
        data.append([P(v, S_CELL_SMALL) for v in row])
    t = LongTable(data, colWidths=widths, repeatRows=1, splitByRow=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, GRAY_200),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRAY_050]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

def _card(label: str, value: str, note: str = "", tone: str = "normal") -> Table:
    bg = colors.white
    edge = GRAY_200
    value_color = BLACK
    if tone == "danger":
        bg, edge, value_color = RED_LIGHT, colors.HexColor("#E2C4C4"), RED
    elif tone == "good":
        bg, edge, value_color = GREEN_LIGHT, colors.HexColor("#CDDCCD"), GREEN

    value_style = ParagraphStyle("CardV", parent=S_CARD_VALUE, textColor=value_color)
    data = [[Paragraph(label.upper(), S_CARD_LABEL)], [Paragraph(value, value_style)]]
    if note:
        data.append([Paragraph(note, S_SMALL)])
    t = Table(data, colWidths=[78 * mm], rowHeights=None)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.6, edge),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def _cards_grid(cards: list[Table]) -> Table:
    rows = [cards[i:i+3] for i in range(0, len(cards), 3)]
    while rows and len(rows[-1]) < 3:
        rows[-1].append(Spacer(1, 1))
    t = Table(rows, colWidths=[82 * mm] * 3, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _standard_table(headers: list[str], rows: Iterable[Iterable[Any]], widths: list[float], small=False) -> Table:
    cell_style = S_CELL_SMALL if small else S_CELL
    data = [[Paragraph(h, S_HEAD) for h in headers]]
    for row in rows:
        data.append([P(v, cell_style) for v in row])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, GRAY_200),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRAY_050]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build_pdf(
    data_inicio: str,
    data_fim: str,
    resumo: dict,
    financeiro: dict,
    mensal: list[dict],
    motivos: list[dict],
    glosas: list[dict],
    produtos: list[dict],
    atendimentos: list[dict] | None = None,
    pacientes: list[dict] | None = None,
    remessas: list[dict] | None = None,
    pagamentos: dict | None = None,
    pagamentos_competencia: list[dict] | None = None,
    pagamentos_eventos: list[dict] | None = None,
    auditoria: dict | None = None,
    detalhado: bool = False,
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=PAGE_SIZE,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"Relatorio Oncologia Convênio Demo {data_inicio} a {data_fim}",
        author="TI - Hospital Demonstrativo",
        subject="Relatorio gerencial de oncologia Convênio Demo",
    )

    story = []
    atendimentos = atendimentos or []
    pacientes = pacientes or []
    remessas = remessas or []
    pagamentos = pagamentos or {}
    pagamentos_competencia = pagamentos_competencia or []
    pagamentos_eventos = pagamentos_eventos or []
    auditoria = auditoria or {}
    emitted = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Report identity block
    hero = Table([
        [
            Paragraph("RELATORIO GERENCIAL", ParagraphStyle(
                "eyebrow", parent=S_SMALL, fontName="Helvetica-Bold",
                textColor=GOLD, fontSize=7.5, leading=9, spaceAfter=3,
            )),
            Paragraph(f"Periodo analisado<br/><b>{data_inicio} a {data_fim}</b>", S_RIGHT),
        ],
        [Paragraph("Oncologia - Convênio Demo", S_TITLE), Paragraph(f"Emitido em<br/><b>{emitted}</b>", S_RIGHT)],
        [Paragraph("Faturamento, remessas, glosas e indicadores assistenciais", S_SUBTITLE), ""],
    ], colWidths=[180 * mm, 75 * mm])
    hero.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("SPAN", (0, 2), (1, 2)),
        ("LINEBELOW", (0, 2), (-1, 2), 1, GOLD),
        ("BOTTOMPADDING", (0, 2), (-1, 2), 8),
    ]))
    story += [hero, Spacer(1, 5 * mm)]

    # Precision note
    note = Table([[Paragraph(
        "<b>Nota de precisao financeira:</b> recebimentos reais usam receipt_date e os valores alocados em "
        "ReceiptAdjustment. O indicador batch_paid_flag da remessa permanece apenas como status operacional. "
        "receipt_date e apresentada como data de recebimento registrada no financeiro, nao como data bancaria.",
        S_BODY,
    )]], colWidths=[255 * mm])
    note.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GOLD_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#DAC79E")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [note, Spacer(1, 5 * mm), Paragraph("Resumo executivo", S_SECTION)]

    fat = _n(financeiro.get("vl_faturado"))
    rem = _n(financeiro.get("vl_remetido"))
    paid = _n(financeiro.get("vl_remessas_pagas"))
    cards = [
        _card("Faturado", brl(fat), f"{integer(financeiro.get('qt_contas'))} contas"),
        _card("Remetido", brl(rem), percent(financeiro.get("pct_remetido_faturado"))),
        _card("Nao remetido", brl(financeiro.get("vl_nao_remetido"))),
        _card("Em remessas pagas", brl(paid), f"{percent((paid/rem*100) if rem else 0)} do remetido", "good"),
        _card("Em remessas nao pagas", brl(financeiro.get("vl_remessas_nao_pagas"))),
        _card("Glosa liquida", brl(financeiro.get("vl_glosa_liquida")), f"{integer(financeiro.get('qt_contas_com_glosa'))} contas", "danger"),
    ]
    story += [_cards_grid(cards), Spacer(1, 4 * mm)]

    assist_cards = [
        _card("Atendimentos faturados", integer(resumo.get("atendimentos_com_faturamento"))),
        _card("Contas oncologicas", integer(resumo.get("contas_onco"))),
        _card("Produtos distintos", integer(resumo.get("produtos_distintos"))),
    ]
    story += [Paragraph("Indicadores assistenciais", S_SECTION), _cards_grid(assist_cards), Spacer(1, 3 * mm)]

    comp_rows = [
        ["Faturado", brl(financeiro.get("vl_faturado")), "Base financeira das contas oncologicas do periodo"],
        ["Remetido", brl(financeiro.get("vl_remetido")), "Contas associadas a remessa"],
        ["Nao remetido", brl(financeiro.get("vl_nao_remetido")), "Contas ainda sem remessa vinculada"],
        ["Remessas marcadas como pagas", brl(financeiro.get("vl_remessas_pagas")), "Status batch_paid_flag='S' - nao equivale a recebimento efetivo"],
        ["Remessas nao pagas", brl(financeiro.get("vl_remessas_nao_pagas")), "Remessas sem status de paga"],
        ["Glosa bruta", brl(financeiro.get("vl_glosa_bruta")), f"{integer(financeiro.get('qt_eventos_glosa'))} eventos"],
        ["Glosa revertida", brl(financeiro.get("vl_glosa_revertida")), "Regra validada para regra demonstrativa de ajuste no fluxo Convênio Demo"],
        ["Glosa liquida", brl(financeiro.get("vl_glosa_liquida")), percent(financeiro.get("pct_glosa_liquida_remetido"), 4) + " do remetido"],
    ]
    composition_block = KeepTogether([
        Paragraph("Composicao financeira", S_SECTION),
        _standard_table(["Indicador", "Valor", "Leitura"], comp_rows, [62 * mm, 43 * mm, 150 * mm]),
        Spacer(1, 6 * mm),
    ])
    story.append(composition_block)

    story += [Spacer(1, 3 * mm), Paragraph("Recebimentos financeiros reais", S_SECTION)]
    story.append(Paragraph(
        "Nesta secao, o periodo e aplicado a receipt_date. A composicao e rastreada por evento financeiro, item faturado, conta, remessa, atendimento e paciente.",
        S_BODY,
    ))
    story.append(Spacer(1, 3 * mm))
    pay_cards = [
        _card("Recebimento financeiro", brl(pagamentos.get("vl_recebido_financeiro")), f"{integer(pagamentos.get('qt_eventos_recebimento'))} eventos", "good"),
        _card("Recebimento base", brl(pagamentos.get("vl_recebido_base")), "Recebimento financeiro menos acrescimos"),
        _card("Acrescimos", brl(pagamentos.get("vl_acrescimo"))),
        _card("Contas recebidas", integer(pagamentos.get("qt_contas_recebidas")), f"{integer(pagamentos.get('qt_remessas_recebidas'))} remessas"),
        _card("Pacientes", integer(pagamentos.get("qt_pacientes")), f"{integer(pagamentos.get('qt_atendimentos'))} atendimentos"),
        _card("Glosa no recebimento", brl(pagamentos.get("vl_glosa_recebimento")), tone="danger"),
    ]
    story += [_cards_grid(pay_cards), Spacer(1, 4 * mm)]

    if pagamentos_competencia:
        comp_pay_rows = []
        for r in pagamentos_competencia:
            comp_pay_rows.append([
                safe(r.get("competencia")), safe(r.get("mes_recebimento")),
                integer(r.get("qt_atendimentos")), integer(r.get("qt_contas")),
                brl(r.get("vl_recebido_financeiro")), brl(r.get("vl_recebido_base")),
                brl(r.get("vl_acrescimo")), brl(r.get("vl_glosa")),
            ])
        story += [Paragraph("Competencia x mes do recebimento", S_SECTION)]
        story.append(_standard_table(
            ["Competencia", "Recebido em", "Atend.", "Contas", "Receb. financeiro", "Receb. base", "Acrescimos", "Glosa"],
            comp_pay_rows,
            [27*mm, 27*mm, 18*mm, 18*mm, 42*mm, 38*mm, 32*mm, 30*mm],
            small=True,
        ))

    # Monthly section follows naturally, using the remaining page space.
    story += [Paragraph("Evolucao mensal", S_SECTION)]
    if mensal:
        monthly_rows = []
        for r in mensal:
            monthly_rows.append([
                safe(r.get("mes")), brl(r.get("vl_faturado")), brl(r.get("vl_remetido")),
                brl(r.get("vl_nao_remetido")), brl(r.get("vl_remessas_pagas")), brl(r.get("vl_remessas_nao_pagas")),
            ])
        story.append(_standard_table(
            ["Competencia", "Faturado", "Remetido", "Nao remetido", "Remessas pagas*", "Remessas nao pagas"],
            monthly_rows,
            [32 * mm, 42 * mm, 42 * mm, 42 * mm, 47 * mm, 50 * mm],
        ))
        story += [Spacer(1, 3 * mm), Paragraph(
            "* O agrupamento mensal acima segue a data de lancamento das contas. A secao de recebimentos usa receipt_date e possui linha temporal propria.",
            S_SMALL,
        )]
    else:
        story.append(Paragraph("Nao houve dados mensais retornados para o periodo selecionado.", S_BODY))

    # Glosas
    story += [Spacer(1, 7 * mm), Paragraph("Glosas por motivo", S_SECTION)]
    if motivos:
        motivo_rows = []
        for r in motivos:
            motivo_rows.append([
                safe(r.get("adjustment_reason_code")), safe(r.get("adjustment_reason_description")),
                integer(r.get("qt_glosas")), integer(r.get("qt_contas")),
                brl(r.get("vl_glosa")), brl(r.get("vl_liquida")),
            ])
        story.append(_standard_table(
            ["Cod.", "Motivo", "Eventos", "Contas", "Glosa bruta", "Glosa liquida"],
            motivo_rows,
            [16 * mm, 125 * mm, 24 * mm, 24 * mm, 34 * mm, 34 * mm],
            small=True,
        ))
    else:
        story.append(Paragraph("Nenhum motivo de glosa retornado para o periodo.", S_BODY))

    if glosas:
        story += [PageBreak(), Paragraph("Eventos de glosa - detalhamento", S_SECTION)]
        detail_rows = []
        for g in glosas:
            detail_rows.append([
                short_date(g.get("adjustment_date")), safe(g.get("account_id")), safe(g.get("encounter_id")),
                safe(g.get("billing_item_code")), safe(g.get("billing_item_description")), safe(g.get("adjustment_reason_description")),
                brl(g.get("vl_glosa")), safe(g.get("status_analitico")),
            ])
        story.append(_standard_table(
            ["Data", "Conta", "Atendimento", "Proced.", "Descricao", "Motivo", "Valor", "Status"],
            detail_rows,
            [22 * mm, 20 * mm, 24 * mm, 20 * mm, 55 * mm, 75 * mm, 25 * mm, 24 * mm],
            small=True,
        ))

    # Detailed reconciliation blocks
    if detalhado:
        story += [PageBreak(), Paragraph("Composicao das remessas", S_SECTION)]
        story.append(Paragraph(
            "Esta secao abre o valor por remessa e mostra quantas contas, atendimentos e pacientes compoem cada total. "
            "O status do BillingBatch continua sendo apenas operacional; recebimentos reais sao conciliados separadamente pela cadeia ReceiptEvent/ReceiptAdjustment.",
            S_BODY,
        ))
        story.append(Spacer(1, 3 * mm))
        if remessas:
            rem_rows = []
            for r in remessas:
                rem_rows.append([
                    safe(r.get("billing_batch_id")), safe(r.get("payer_batch_reference")),
                    short_date(r.get("billing_batch_close_date")), safe(r.get("batch_paid_flag")),
                    integer(r.get("qt_contas")), integer(r.get("qt_atendimentos")), integer(r.get("qt_pacientes")),
                    brl(r.get("vl_faturado")), brl(r.get("vl_recebido_base")), brl(r.get("vl_saldo_estimado")),
                    safe(r.get("status_recebimento")),
                ])
            story.append(_standard_table(
                ["Remessa", "Nr. convenio", "Fechamento", "Paga*", "Contas", "Atend.", "Pacientes", "Faturado", "Receb. base", "Saldo", "Status"],
                rem_rows,
                [17*mm, 25*mm, 21*mm, 12*mm, 16*mm, 16*mm, 18*mm, 29*mm, 29*mm, 27*mm, 43*mm],
                small=True,
            ))
        else:
            story.append(Paragraph("Detalhamento de remessas indisponivel para esta execucao.", S_BODY))

        story += [PageBreak(), Paragraph("Pacientes - consolidacao do periodo", S_SECTION)]
        story.append(Paragraph(
            "Totais por paciente com quantidade de atendimentos/contas, faturamento, glosa e valor pos-glosa. "
            "Quando disponivel, custo de medicamento vem de fonte privada de custo e nao representa o custo hospitalar total.",
            S_BODY,
        ))
        story.append(Spacer(1, 3 * mm))
        if pacientes:
            pac_rows = []
            for r in pacientes:
                pac_rows.append([
                    safe(r.get("patient_id")), safe(r.get("patient_name")), integer(r.get("qt_atendimentos")),
                    integer(r.get("qt_contas")), brl(r.get("vl_faturado")), brl(r.get("vl_glosa_liquida")),
                    brl(r.get("vl_recebido_base")), brl(r.get("vl_saldo_estimado")),
                    brl(r.get("vl_medio_por_atendimento")),
                    brl(r.get("medication_cost_amount")) if "medication_cost_amount" in r else "-",
                ])
            story.append(_standard_table(
                ["Cod.", "Paciente", "Atend.", "Contas", "Faturado", "Glosa", "Receb. base", "Saldo", "Media/atend.", "Custo med.*"],
                pac_rows,
                [15*mm, 52*mm, 16*mm, 16*mm, 28*mm, 24*mm, 29*mm, 27*mm, 28*mm, 28*mm],
                small=True,
            ))
        else:
            story.append(Paragraph("Detalhamento por paciente indisponivel para esta execucao.", S_BODY))

        story += [PageBreak(), Paragraph("Atendimentos e contas - rastreabilidade", S_SECTION)]
        if atendimentos:
            atend_rows = []
            for r in atendimentos:
                atend_rows.append([
                    safe(r.get("patient_name")), safe(r.get("encounter_id")), safe(r.get("account_id")),
                    short_date(r.get("encounter_date")), safe(r.get("billing_batch_id")), safe(r.get("batch_paid_flag")),
                    brl(r.get("vl_faturado")), brl(r.get("vl_glosa_liquida")), brl(r.get("vl_recebido_base")),
                    brl(r.get("vl_saldo_estimado")), safe(r.get("status_financeiro")),
                ])
            story.append(_standard_table(
                ["Paciente", "Atendimento", "Conta", "Data atend.", "Remessa", "Paga*", "Faturado", "Glosa", "Receb. base", "Saldo", "Status"],
                atend_rows,
                [43*mm, 20*mm, 18*mm, 20*mm, 17*mm, 12*mm, 27*mm, 23*mm, 28*mm, 26*mm, 40*mm],
                small=True,
            ))
            story += [Spacer(1, 3*mm), Paragraph(
                "* Paga = status operacional do BillingBatch e permanece apenas como status operacional. Receb. base usa os eventos financeiros conciliados. ", S_SMALL,
            )]
        else:
            story.append(Paragraph("Detalhamento por atendimento indisponivel para esta execucao.", S_BODY))

    if detalhado and pagamentos_eventos:
        story += [PageBreak(), Paragraph("Eventos de recebimento - composicao", S_SECTION)]
        ev_rows = []
        for r in pagamentos_eventos:
            ev_rows.append([
                safe(r.get("receipt_event_id")), short_date(r.get("receipt_date")),
                integer(r.get("qt_remessas_onco")), integer(r.get("qt_contas_onco")),
                integer(r.get("qt_pacientes_onco")), brl(r.get("vl_evento_total")),
                brl(r.get("vl_onco_recebido")), percent(r.get("pct_onco_evento")),
            ])
        story.append(_standard_table(
            ["Evento", "Data receb.", "Remessas", "Contas", "Pacientes", "Evento total", "Parcela onco", "% onco"],
            ev_rows, [21*mm, 25*mm, 22*mm, 19*mm, 21*mm, 38*mm, 38*mm, 22*mm], small=True,
        ))

    if detalhado and auditoria:
        story += [Spacer(1, 7*mm), Paragraph("Auditoria automatica", S_SECTION)]
        aud_rows = [
            ["Contas sem nota fiscal", integer(auditoria.get("qt_sem_nota"))],
            ["Contas sem recebimento", integer(auditoria.get("qt_sem_recebimento"))],
            ["Remessas pagas sem recebimento", integer(auditoria.get("qt_remessa_paga_sem_recebimento"))],
            ["Recebimento maior que faturado", integer(auditoria.get("qt_receb_maior_faturado"))],
            ["Contas parcialmente recebidas", integer(auditoria.get("qt_parcialmente_recebida"))],
            ["Contas com multiplos recebimentos", integer(auditoria.get("qt_multiplos_recebimentos"))],
            ["Saldo estimado", brl(auditoria.get("vl_saldo_estimado"))],
        ]
        story.append(_standard_table(["Regra", "Resultado"], aud_rows, [160*mm, 60*mm]))

    # Products
    story += [PageBreak(), Paragraph("Produtos observados no atendimento oncologico", S_SECTION)]
    story.append(Paragraph(
        "A tabela abaixo apresenta os produtos retornados pelo modelo vigente. A classificacao deve ser lida como evidência operacional do periodo analisado, nao como cadastro mestre de oncologia.",
        S_BODY,
    ))
    story.append(Spacer(1, 3 * mm))
    if produtos:
        prod_rows = []
        for p in produtos:
            prod_rows.append([
                safe(p.get("product_id")), safe(p.get("product_description")), safe(p.get("is_medication")),
                integer(p.get("mov_onco")), integer(p.get("mov_total")), percent(p.get("pct_onco")),
                safe(p.get("classificacao")), safe(p.get("confianca")),
            ])
        story.append(_standard_table(
            ["Cod.", "Produto", "Med.", "Mov. onco", "Mov. base", "% onco", "Classificacao", "Confianca"],
            prod_rows,
            [18 * mm, 82 * mm, 15 * mm, 24 * mm, 24 * mm, 21 * mm, 56 * mm, 24 * mm],
            small=True,
        ))
    else:
        story.append(Paragraph("Nenhum produto retornado para o periodo.", S_BODY))

    # Methodology / provenance
    story += [PageBreak(), Paragraph("Metodologia e rastreabilidade", S_SECTION)]
    methodological = [
        "O relatorio consolida dados assistenciais e financeiros vinculados aos atendimentos oncologicos do convenio Convênio Demo.",
        "As consultas sao somente leitura e o periodo operacional permanece limitado a 93 dias por execucao.",
        "Faturamento, remessa e recebimento sao tratados como eventos distintos. O status do BillingBatch permanece separado dos eventos financeiros.",
        "Recebimentos reais usam receipt_date e ReceiptAdjustment; InvoiceItem e InvoiceItem fornecem conta, remessa, competencia e rastreabilidade assistencial.",
        "receipt_date e apresentada como data de recebimento registrada no financeiro, sem inferir data bancaria quando essa informacao nao esta comprovada.",
        "Glosas sao vinculadas diretamente as contas oncologicas identificadas no periodo. O regra demonstrativa de ajuste e tratado como revertido apenas na regra previamente validada para este fluxo Convênio Demo.",
    ]
    for item in methodological:
        story.append(Paragraph(f"• {item}", S_BODY))
        story.append(Spacer(1, 2 * mm))

    sign = Table([
        [Paragraph("TI - Hospital Demonstrativo", ParagraphStyle("Sig1", parent=S_BODY, fontName="Helvetica-Bold"))],
        [Paragraph("Portfolio demonstrativo", S_BODY)],
    ], colWidths=[90 * mm])
    sign.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story += [Spacer(1, 8 * mm), sign]

    doc.build(story, onFirstPage=_page_header_footer, onLaterPages=_page_header_footer)
    return buf.getvalue()


def build_account_pdf(payload: dict) -> bytes:
    """Relatório próprio para conferência de uma conta ambulatorial oncológica."""
    conta = payload.get("conta") or {}
    itens = payload.get("itens") or []
    recebimentos = payload.get("recebimentos") or []
    glosas = payload.get("glosas") or []

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=PAGE_SIZE,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"Conta oncológica {safe(conta.get('account_id'))}",
        author="TI - Hospital Demonstrativo",
        subject="Detalhamento de conta oncológica",
    )
    emitted = datetime.now().strftime("%d/%m/%Y %H:%M")
    story = []
    payer_id = conta.get("payer_id")
    convenio_label = "Convênio Demo · Convênio 11" if str(payer_id) == "11" else f"Convênio {safe(payer_id)}"
    remetida = bool(conta.get("billing_batch_id"))
    remessa_label = safe(conta.get("billing_batch_id")) if remetida else "Não remetida"
    payer_reference_label = safe(conta.get("payer_batch_reference")) if remetida else "Não remetida"
    fechamento_label = short_date(conta.get("billing_batch_close_date")) if remetida else "Não remetida"
    story += [
        Paragraph("DETALHAMENTO DE CONTA", ParagraphStyle("AccEyebrow", parent=S_SMALL, fontName="Helvetica-Bold", textColor=GOLD)),
        Paragraph(f"Conta {safe(conta.get('account_id'))} · Oncologia", S_TITLE),
        Paragraph(f"Relatório interno de conferência · Emitido em {emitted}", S_SUBTITLE),
        Spacer(1, 4 * mm),
    ]

    info = [
        ["Paciente", safe(conta.get("patient_name")), "Código paciente", safe(conta.get("patient_id"))],
        ["Atendimento", safe(conta.get("encounter_id")), "Data atendimento", short_date(conta.get("encounter_date"))],
        ["Convênio", convenio_label, "Remessa", remessa_label],
        ["Nº remessa convênio", payer_reference_label, "Fechamento", fechamento_label],
        ["Status", safe(conta.get("status_financeiro")).replace("_", " "), "Último recebimento", short_date(conta.get("ultimo_recebimento"))],
    ]
    t = Table([[P(c, S_CELL) for c in row] for row in info], colWidths=[34*mm, 94*mm, 40*mm, 87*mm])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), .25, GRAY_200),
        ("BACKGROUND", (0,0), (0,-1), GRAY_100),
        ("BACKGROUND", (2,0), (2,-1), GRAY_100),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [t, Spacer(1, 5*mm)]

    cards = [
        _card("Faturado", brl(conta.get("vl_faturado"))),
        _card("Recebido base", brl(conta.get("vl_recebido_base")), "Sem acréscimos"),
        _card("Saldo estimado", brl(conta.get("vl_saldo_estimado"))),
        _card("Glosa líquida", brl(conta.get("vl_glosa_liquida")), tone="danger" if _n(conta.get("vl_glosa_liquida")) else "normal"),
        _card("Acréscimos", brl(conta.get("vl_acrescimo_recebimento"))),
        _card("Eventos de recebimento", integer(conta.get("qt_eventos_recebimento"))),
    ]
    story += [_cards_grid(cards), Spacer(1, 3*mm)]

    story += [Paragraph("Itens da conta", S_SECTION)]
    item_rows = []
    for i in itens:
        item_rows.append([
            safe(i.get("line_item_id")), short_date(i.get("session_date") or i.get("production_date")),
            safe(i.get("billing_item_code")), safe(i.get("billing_item_description")),
            safe(i.get("quantity")), brl(i.get("unit_amount")), brl(i.get("account_total_amount")),
        ])
    story += [_account_items_table(
        ["Lanç.", "Data", "Código", "Descrição", "Qtde", "Valor unit.", "Valor total"],
        item_rows,
        [15*mm, 22*mm, 24*mm, 112*mm, 16*mm, 31*mm, 31*mm],
    ), Spacer(1, 5*mm)]

    if recebimentos:
        story += [Paragraph("Recebimentos vinculados", S_SECTION)]
        rows = [[safe(r.get("receipt_event_id")), short_date(r.get("receipt_date")), brl(r.get("vl_recebido_base")), brl(r.get("vl_acrescimo")), brl(r.get("vl_glosa"))] for r in recebimentos]
        story += [_standard_table(["Evento", "Data financeira", "Recebido base", "Acréscimo", "Glosa"], rows, [35*mm, 42*mm, 55*mm, 55*mm, 55*mm]), Spacer(1, 5*mm)]

    if glosas:
        story += [Paragraph("Glosas", S_SECTION)]
        rows = [[short_date(g.get("adjustment_date")), safe(g.get("billing_item_code")), safe(g.get("billing_item_description")), safe(g.get("adjustment_reason_description")), brl(g.get("vl_glosa"))] for g in glosas]
        story += [_standard_table(["Data", "Código", "Procedimento", "Motivo", "Valor"], rows, [24*mm, 24*mm, 86*mm, 86*mm, 35*mm], small=True)]

    story += [Spacer(1, 5*mm), Paragraph(
        "Fonte dos itens: InvoiceItem + BillingItem. A data de recebimento exibida corresponde ao registro financeiro do MV e não deve ser interpretada como data de crédito bancário.",
        S_SMALL,
    )]
    doc.build(story, onFirstPage=_account_page_header_footer, onLaterPages=_account_page_header_footer)
    return buf.getvalue()
