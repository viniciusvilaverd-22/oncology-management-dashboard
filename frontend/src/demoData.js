const viteEnv = import.meta.env || {};
export const DEMO_MODE = viteEnv.VITE_DEMO_MODE === "true";

export const demoSession = {
  user: {
    id: 1,
    username: "portfolio",
    display_name: "Portfolio Demo",
    email: "portfolio@example.com",
    role: "FATURAMENTO",
    active: true,
    all_convenios: true,
    default_convenio: 100,
    must_change_password: false,
  },
  csrf_token: "demo-csrf",
  expires_at: "2099-12-31T23:59:59Z",
};

export const demoConvenios = [
  {
    payer_id: 100,
    payer_name: "Convênio Demonstrativo",
    modelo_homologado: true,
    modelo: "ONCOLOGY_DEMO",
  },
];

const patients = [
  { patient_id: 1001, patient_name: "Paciente Demo 01" },
  { patient_id: 1002, patient_name: "Paciente Demo 02" },
  { patient_id: 1003, patient_name: "Paciente Demo 03" },
  { patient_id: 1004, patient_name: "Paciente Demo 04" },
  { patient_id: 1005, patient_name: "Paciente Demo 05" },
];

const accounts = [
  {
    patient_id: 1001, patient_name: "Paciente Demo 01", encounter_id: 51001, account_id: 81001,
    billing_batch_id: 9101, encounter_date: "2026-07-08", competence_date: "2026-07-01",
    vl_faturado: 18450, vl_recebido_base: 18450, vl_acrescimo_recebimento: 320,
    vl_glosa_liquida: 0, vl_saldo_estimado: 0, status_financeiro: "RECEBIDA",
    primeiro_recebimento: "2026-08-15", ultimo_recebimento: "2026-08-15",
  },
  {
    patient_id: 1002, patient_name: "Paciente Demo 02", encounter_id: 51002, account_id: 81002,
    billing_batch_id: 9102, encounter_date: "2026-07-16", competence_date: "2026-07-01",
    vl_faturado: 22100, vl_recebido_base: 19500, vl_acrescimo_recebimento: 180,
    vl_glosa_liquida: 600, vl_saldo_estimado: 2600, status_financeiro: "PARCIALMENTE_RECEBIDA_COM_GLOSA",
    primeiro_recebimento: "2026-08-28", ultimo_recebimento: "2026-09-19",
  },
  {
    patient_id: 1003, patient_name: "Paciente Demo 03", encounter_id: 51003, account_id: 81003,
    billing_batch_id: 9103, encounter_date: "2026-08-04", competence_date: "2026-08-01",
    vl_faturado: 15780, vl_recebido_base: 15180, vl_acrescimo_recebimento: 210,
    vl_glosa_liquida: 600, vl_saldo_estimado: 600, status_financeiro: "RECEBIDA_COM_GLOSA",
    primeiro_recebimento: "2026-09-12", ultimo_recebimento: "2026-09-12",
  },
  {
    patient_id: 1004, patient_name: "Paciente Demo 04", encounter_id: 51004, account_id: 81004,
    billing_batch_id: 9104, encounter_date: "2026-08-21", competence_date: "2026-08-01",
    vl_faturado: 26640, vl_recebido_base: 13200, vl_acrescimo_recebimento: 90,
    vl_glosa_liquida: 0, vl_saldo_estimado: 13440, status_financeiro: "PARCIALMENTE_RECEBIDA",
    primeiro_recebimento: "2026-09-30", ultimo_recebimento: "2026-09-30",
  },
  {
    patient_id: 1005, patient_name: "Paciente Demo 05", encounter_id: 51005, account_id: 81005,
    billing_batch_id: 9105, encounter_date: "2026-09-05", competence_date: "2026-09-01",
    vl_faturado: 19820, vl_recebido_base: 0, vl_acrescimo_recebimento: 0,
    vl_glosa_liquida: 0, vl_saldo_estimado: 19820, status_financeiro: "SEM_RECEBIMENTO",
    primeiro_recebimento: null, ultimo_recebimento: null,
  },
];

const accountItems = {
  81001: [
    { line_item_id: 1, session_date: "2026-07-08", billing_item_code: "PROC-101", billing_item_description: "Terapia antineoplásica - sessão", quantity: 1, unit_amount: 12800, account_total_amount: 12800, authorization_id: "GUIA-001" },
    { line_item_id: 2, session_date: "2026-07-08", billing_item_code: "MAT-210", billing_item_description: "Materiais e medicamentos", quantity: 1, unit_amount: 5650, account_total_amount: 5650, authorization_id: "GUIA-001" },
  ],
  81002: [
    { line_item_id: 3, session_date: "2026-07-16", billing_item_code: "PROC-102", billing_item_description: "Terapia antineoplásica - sessão", quantity: 1, unit_amount: 14600, account_total_amount: 14600, authorization_id: "GUIA-002" },
    { line_item_id: 4, session_date: "2026-07-16", billing_item_code: "MAT-211", billing_item_description: "Materiais e medicamentos", quantity: 1, unit_amount: 7500, account_total_amount: 7500, authorization_id: "GUIA-002" },
  ],
  81003: [
    { line_item_id: 5, session_date: "2026-08-04", billing_item_code: "PROC-103", billing_item_description: "Terapia antineoplásica - sessão", quantity: 1, unit_amount: 10480, account_total_amount: 10480, authorization_id: "GUIA-003" },
    { line_item_id: 6, session_date: "2026-08-04", billing_item_code: "MAT-212", billing_item_description: "Materiais e medicamentos", quantity: 1, unit_amount: 5300, account_total_amount: 5300, authorization_id: "GUIA-003" },
  ],
  81004: [
    { line_item_id: 7, session_date: "2026-08-21", billing_item_code: "PROC-104", billing_item_description: "Terapia antineoplásica - sessão", quantity: 1, unit_amount: 17400, account_total_amount: 17400, authorization_id: "GUIA-004" },
    { line_item_id: 8, session_date: "2026-08-21", billing_item_code: "MAT-213", billing_item_description: "Materiais e medicamentos", quantity: 1, unit_amount: 9240, account_total_amount: 9240, authorization_id: "GUIA-004" },
  ],
  81005: [
    { line_item_id: 9, session_date: "2026-09-05", billing_item_code: "PROC-105", billing_item_description: "Terapia antineoplásica - sessão", quantity: 1, unit_amount: 13120, account_total_amount: 13120, authorization_id: "GUIA-005" },
    { line_item_id: 10, session_date: "2026-09-05", billing_item_code: "MAT-214", billing_item_description: "Materiais e medicamentos", quantity: 1, unit_amount: 6700, account_total_amount: 6700, authorization_id: "GUIA-005" },
  ],
};

const paymentAccounts = accounts
  .filter((row) => row.vl_recebido_base > 0)
  .map((row, index) => ({
    ...row,
    vl_recebido_financeiro_periodo: row.vl_recebido_base + row.vl_acrescimo_recebimento,
    vl_recebido_base_periodo: row.vl_recebido_base,
    vl_recebido_base_acum: row.vl_recebido_base,
    vl_glosa_periodo: row.vl_glosa_liquida,
    vl_glosa_acum: row.vl_glosa_liquida,
    vl_saldo_glosado: Math.min(row.vl_saldo_estimado, row.vl_glosa_liquida),
    vl_saldo_financeiro_aberto: Math.max(row.vl_saldo_estimado - row.vl_glosa_liquida, 0),
    status_recebimento: row.status_financeiro,
    qt_eventos_acumulados: index === 1 ? 2 : 1,
    dias_atendimento_recebimento: [38, 65, 39, 40][index],
    primeiro_recebimento_no_periodo: row.primeiro_recebimento,
    ultimo_recebimento_no_periodo: row.ultimo_recebimento,
  }));

const receiptEvents = [
  { receipt_event_id: 70001, receipt_date: "2026-08-15", qt_remessas_onco: 1, qt_contas_onco: 1, qt_pacientes_onco: 1, vl_evento_total: 28900, vl_onco_recebido: 18770, vl_onco_acrescimo: 320, pct_onco_evento: 64.95 },
  { receipt_event_id: 70002, receipt_date: "2026-08-28", qt_remessas_onco: 1, qt_contas_onco: 1, qt_pacientes_onco: 1, vl_evento_total: 34800, vl_onco_recebido: 12180, vl_onco_acrescimo: 80, pct_onco_evento: 35.0 },
  { receipt_event_id: 70003, receipt_date: "2026-09-12", qt_remessas_onco: 1, qt_contas_onco: 1, qt_pacientes_onco: 1, vl_evento_total: 24600, vl_onco_recebido: 15390, vl_onco_acrescimo: 210, pct_onco_evento: 62.56 },
  { receipt_event_id: 70004, receipt_date: "2026-09-19", qt_remessas_onco: 1, qt_contas_onco: 1, qt_pacientes_onco: 1, vl_evento_total: 19800, vl_onco_recebido: 7500, vl_onco_acrescimo: 100, pct_onco_evento: 37.88 },
  { receipt_event_id: 70005, receipt_date: "2026-09-30", qt_remessas_onco: 1, qt_contas_onco: 1, qt_pacientes_onco: 1, vl_evento_total: 32100, vl_onco_recebido: 13290, vl_onco_acrescimo: 90, pct_onco_evento: 41.4 },
];

const eventItems = {
  70001: [{ invoice_item_id: 30001, patient_name: "Paciente Demo 01", encounter_id: 51001, account_id: 81001, billing_batch_id: 9101, competence_date: "2026-07-01", vl_faturado: 18450, vl_recebido_financeiro: 18770, vl_acrescimo: 320, vl_glosa_recebimento: 0 }],
  70002: [{ invoice_item_id: 30002, patient_name: "Paciente Demo 02", encounter_id: 51002, account_id: 81002, billing_batch_id: 9102, competence_date: "2026-07-01", vl_faturado: 22100, vl_recebido_financeiro: 12180, vl_acrescimo: 80, vl_glosa_recebimento: 300 }],
  70003: [{ invoice_item_id: 30003, patient_name: "Paciente Demo 03", encounter_id: 51003, account_id: 81003, billing_batch_id: 9103, competence_date: "2026-08-01", vl_faturado: 15780, vl_recebido_financeiro: 15390, vl_acrescimo: 210, vl_glosa_recebimento: 600 }],
  70004: [{ invoice_item_id: 30004, patient_name: "Paciente Demo 02", encounter_id: 51002, account_id: 81002, billing_batch_id: 9102, competence_date: "2026-07-01", vl_faturado: 10000, vl_recebido_financeiro: 7500, vl_acrescimo: 100, vl_glosa_recebimento: 300 }],
  70005: [{ invoice_item_id: 30005, patient_name: "Paciente Demo 04", encounter_id: 51004, account_id: 81004, billing_batch_id: 9104, competence_date: "2026-08-01", vl_faturado: 26640, vl_recebido_financeiro: 13290, vl_acrescimo: 90, vl_glosa_recebimento: 0 }],
};

const denials = [
  { cd_glosas: 60001, adjustment_date: "2026-09-18", account_id: 81002, encounter_id: 51002, billing_item_description: "Terapia antineoplásica - sessão", adjustment_reason_description: "Divergência documental", vl_glosa: 600, status_analitico: "ATIVA" },
  { cd_glosas: 60002, adjustment_date: "2026-09-14", account_id: 81003, encounter_id: 51003, billing_item_description: "Materiais e medicamentos", adjustment_reason_description: "Validação contratual", vl_glosa: 600, status_analitico: "ATIVA" },
];

const monthlyProduction = [
  { mes: "2026-07", vl_faturado: 40550, vl_remetido: 40550, vl_remessas_pagas: 37950 },
  { mes: "2026-08", vl_faturado: 42420, vl_remetido: 42420, vl_remessas_pagas: 28380 },
  { mes: "2026-09", vl_faturado: 19820, vl_remetido: 19820, vl_remessas_pagas: 0 },
];

const billingMonthly = [
  { competencia: "2026-07", vl_faturamento_competencia: 39200, vl_ambulatorial: 39200, vl_hospitalar: 0, qt_itens: 24, qt_contas: 2, qt_atendimentos: 2, qt_remessas: 2 },
  { competencia: "2026-08", vl_faturamento_competencia: 43800, vl_ambulatorial: 43800, vl_hospitalar: 0, qt_itens: 26, qt_contas: 2, qt_atendimentos: 2, qt_remessas: 2 },
  { competencia: "2026-09", vl_faturamento_competencia: 20500, vl_ambulatorial: 20500, vl_hospitalar: 0, qt_itens: 12, qt_contas: 1, qt_atendimentos: 1, qt_remessas: 1 },
];

const receiptByCompetence = [
  { competencia: "2026-07", mes_recebimento: "2026-08", vl_recebido_financeiro: 30950, vl_glosa: 300 },
  { competencia: "2026-07", mes_recebimento: "2026-09", vl_recebido_financeiro: 7600, vl_glosa: 300 },
  { competencia: "2026-08", mes_recebimento: "2026-09", vl_recebido_financeiro: 28680, vl_glosa: 600 },
];

const historicalCompetences = [
  { competencia: "2026-07", qt_contas: 2, vl_faturado: 40550, vl_recebido_financeiro: 38550, vl_recebido_base: 37950, vl_glosa: 600, vl_em_aberto: 2000, mes_recebimento: "2026-08", vl_recebido_mes: 30950, vl_recebido_base_mes: 30550, vl_glosa_mes: 300 },
  { competencia: "2026-07", qt_contas: 2, vl_faturado: 40550, vl_recebido_financeiro: 38550, vl_recebido_base: 37950, vl_glosa: 600, vl_em_aberto: 2000, mes_recebimento: "2026-09", vl_recebido_mes: 7600, vl_recebido_base_mes: 7400, vl_glosa_mes: 300 },
  { competencia: "2026-08", qt_contas: 2, vl_faturado: 42420, vl_recebido_financeiro: 28680, vl_recebido_base: 28380, vl_glosa: 600, vl_em_aberto: 13440, mes_recebimento: "2026-09", vl_recebido_mes: 28680, vl_recebido_base_mes: 28380, vl_glosa_mes: 600 },
  { competencia: "2026-09", qt_contas: 1, vl_faturado: 19820, vl_recebido_financeiro: 0, vl_recebido_base: 0, vl_glosa: 0, vl_em_aberto: 19820, mes_recebimento: null, vl_recebido_mes: 0, vl_recebido_base_mes: 0, vl_glosa_mes: 0 },
];

const products = [
  { product_id: 2001, product_description: "Medicamento antineoplásico A", is_medication: "S", mov_onco: 22, mov_total: 28, pct_onco: 78.57, classificacao: "Alta participação", confianca: "Alta" },
  { product_id: 2002, product_description: "Medicamento de suporte B", is_medication: "S", mov_onco: 17, mov_total: 42, pct_onco: 40.48, classificacao: "Participação moderada", confianca: "Alta" },
  { product_id: 2003, product_description: "Material assistencial C", is_medication: "N", mov_onco: 11, mov_total: 74, pct_onco: 14.86, classificacao: "Uso compartilhado", confianca: "Média" },
];

const patientRows = patients.map((patient) => {
  const rows = accounts.filter((a) => a.patient_id === patient.patient_id);
  const faturado = rows.reduce((sum, a) => sum + a.vl_faturado, 0);
  const recebido = rows.reduce((sum, a) => sum + a.vl_recebido_base, 0);
  const acrescimo = rows.reduce((sum, a) => sum + a.vl_acrescimo_recebimento, 0);
  const glosa = rows.reduce((sum, a) => sum + a.vl_glosa_liquida, 0);
  const saldo = rows.reduce((sum, a) => sum + a.vl_saldo_estimado, 0);
  return {
    ...patient,
    qt_atendimentos: rows.length,
    qt_contas: rows.length,
    qt_remessas: new Set(rows.map((a) => a.billing_batch_id)).size,
    vl_faturado: faturado,
    vl_recebido_base: recebido,
    vl_acrescimo_recebimento: acrescimo,
    vl_glosa_liquida: glosa,
    vl_saldo_estimado: saldo,
    vl_medio_por_atendimento: rows.length ? faturado / rows.length : 0,
    vl_recebido_medio_atendimento: rows.length ? recebido / rows.length : 0,
  };
});

const auditDetails = [
  { tipo: "SEM_RECEBIMENTO", ...accounts[4], batch_paid_flag: "N", qt_eventos_recebimento: 0, vl_recebido_base: 0, vl_glosa_recebimento: 0, vl_saldo_financeiro_aberto: 19820, vl_saldo_glosado: 0 },
  { tipo: "RECEBIMENTO_PARCIAL", ...accounts[3], batch_paid_flag: "N", qt_eventos_recebimento: 1, vl_glosa_recebimento: 0, vl_saldo_financeiro_aberto: 13440, vl_saldo_glosado: 0 },
  { tipo: "GLOSA_ATIVA", ...accounts[1], batch_paid_flag: "S", qt_eventos_recebimento: 2, vl_glosa_recebimento: 600, vl_saldo_financeiro_aberto: 2000, vl_saldo_glosado: 600 },
];

function accountDetail(id) {
  const account = accounts.find((row) => row.account_id === Number(id)) || accounts[0];
  const receipts = paymentAccounts
    .filter((row) => row.account_id === account.account_id)
    .map((row, idx) => ({
      receipt_event_id: 70001 + idx,
      receipt_date: row.ultimo_recebimento,
      vl_recebido_base: row.vl_recebido_base,
      vl_acrescimo: row.vl_acrescimo_recebimento,
      vl_glosa: row.vl_glosa_liquida,
    }));
  return {
    conta: account,
    itens: accountItems[account.account_id] || [],
    recebimentos: receipts,
    glosas: denials.filter((row) => row.account_id === account.account_id),
    fonte_itens: "Demo dataset",
    rotulo_recebimento: "Data de recebimento demonstrativa",
  };
}

function comparison() {
  return {
    periodo_atual: { inicio: "2026-07-01", fim: "2026-09-30" },
    periodo_anterior: { inicio: "2026-04-01", fim: "2026-06-30" },
    metricas: [
      { indicador: "Faturado", anterior: 91300, atual: 102790, variacao_pct: 12.58 },
      { indicador: "Remetido", anterior: 88700, atual: 102790, variacao_pct: 15.88 },
      { indicador: "Glosa líquida", anterior: 1760, atual: 1200, variacao_pct: -31.82 },
      { indicador: "Recebimento financeiro", anterior: 67100, atual: 67230, variacao_pct: 0.19 },
      { indicador: "Recebimento base", anterior: 66100, atual: 66330, variacao_pct: 0.35 },
      { indicador: "Contas recebidas", anterior: 3, atual: 4, variacao_pct: 33.33 },
    ],
    nota: "Dados sintéticos para demonstração de portfólio.",
  };
}

export function demoResponse(path) {
  const url = new URL(path, "http://portfolio.demo");
  const p = url.pathname;

  if (p === "/api/onco/capabilities") {
    return { pacientes: true, custo_medicamento: false, recebimento_efetivo: true, periodo_maximo_dias: 365, demo: true };
  }
  if (p === "/api/onco/resumo") {
    return { atendimentos_com_faturamento: 5, contas_onco: 5, produtos_distintos: 3 };
  }
  if (p === "/api/onco/financeiro") {
    return {
      qt_atendimentos: 5, qt_contas: 5, qt_remessas: 5, qt_contas_com_glosa: 2,
      vl_faturado: 102790, vl_remetido: 102790, vl_nao_remetido: 0,
      vl_remessas_pagas: 66330, vl_remessas_nao_pagas: 36460,
      vl_glosa_bruta: 1200, vl_glosa_liquida: 1200,
      pct_remetido_faturado: 100, pct_glosa_liquida_remetido: 1.17,
      semantica_periodo: "Dataset sintético: produção, faturamento e recebimento preservam referências temporais distintas.",
    };
  }
  if (p === "/api/onco/financeiro/mensal") return monthlyProduction;

  if (p === "/api/onco/faturamento-competencia/resumo") {
    return {
      vl_faturamento_competencia: 103500, vl_ambulatorial: 103500, vl_hospitalar: 0,
      qt_itens: 62, qt_itens_ambulatorial: 62, qt_itens_hospitalar: 0,
      qt_contas: 5, qt_atendimentos: 5, qt_remessas: 5, qt_setores: 1,
      setores_aplicados: [10],
    };
  }
  if (p === "/api/onco/faturamento-competencia/mensal") return billingMonthly;
  if (p === "/api/onco/faturamento-competencia/setores") {
    return [{ sector_id: 10, sector_name: "Oncologia Demo", vl_faturamento_competencia: 103500, vl_ambulatorial: 103500, vl_hospitalar: 0, qt_itens: 62, qt_contas: 5, qt_atendimentos: 5, qt_remessas: 5 }];
  }

  if (p === "/api/onco/resumo-integrado") {
    return {
      versao_modelo: "demo",
      setores: [10],
      producao: { valor_contas: 102790, valor_remetido: 102790, valor_nao_remetido: 0, qt_atendimentos: 5, qt_contas: 5, qt_remessas: 5 },
      faturamento_competencia: { valor: 103500, ambulatorial: 103500, hospitalar: 0, qt_itens: 62, qt_contas: 5, qt_atendimentos: 5, qt_remessas: 5 },
      recebimentos: { recebido_financeiro: 67230, recebido_base: 66330, acrescimos: 900, glosa_no_recebimento: 1200, qt_eventos: 5, qt_contas: 4, qt_pacientes: 4 },
      pendencias_recebimentos: { saldo_financeiro_aberto: 15440, saldo_glosado: 1200, qt_recebidas: 1, qt_recebidas_com_glosa: 1, qt_parciais: 2 },
      qualidade_producao: { qt_sem_nota: 1, qt_sem_recebimento: 1, qt_remessa_paga_sem_recebimento: 0, qt_receb_maior_faturado: 0 },
      alertas: [
        { nivel: "atencao", tipo: "SALDO_FINANCEIRO_ABERTO", valor: 15440, texto: "Há saldo financeiro aberto nas contas recebidas no período demonstrativo." },
        { nivel: "atencao", tipo: "SALDO_GLOSADO", valor: 1200, texto: "Há saldo glosado nas contas recebidas no período demonstrativo." },
      ],
      nota_integracao: "Dataset sintético para demonstração. As métricas preservam suas datas de referência.",
    };
  }

  if (p === "/api/onco/pagamentos/resumo") {
    return {
      vl_recebido_financeiro: 67230, vl_recebido_base: 66330, vl_acrescimo: 900,
      vl_glosa_recebimento: 1200, qt_eventos_recebimento: 5, qt_contas_recebidas: 4,
      qt_remessas_recebidas: 4, qt_atendimentos: 4, qt_pacientes: 4,
      qt_itens_multiplos_recebimentos: 1, max_recebimentos_por_item: 2,
    };
  }
  if (p === "/api/onco/pagamentos/competencia") return receiptByCompetence;
  if (p === "/api/onco/historico-competencias") return historicalCompetences;
  if (p === "/api/onco/pagamentos/aging") {
    return { dias_medio: 45.5, dias_p50: 39, dias_p90: 65, pct_acima_90: 0, qt_ate_30: 0, qt_31_60: 3, qt_61_90: 1, qt_acima_90: 0 };
  }
  if (/^\/api\/onco\/pagamentos\/eventos\/\d+\/itens$/.test(p)) {
    const id = Number(p.split("/")[5]);
    return eventItems[id] || [];
  }
  if (p === "/api/onco/pagamentos/eventos") return receiptEvents;
  if (p === "/api/onco/pagamentos/contas") return paymentAccounts;

  if (p === "/api/onco/atendimentos") return accounts;
  if (p === "/api/onco/pacientes") return patientRows;
  if (/^\/api\/onco\/pacientes\/\d+\/contas$/.test(p)) {
    const id = Number(p.split("/")[4]);
    return accounts.filter((row) => row.patient_id === id);
  }
  if (/^\/api\/onco\/contas\/\d+$/.test(p)) {
    return accountDetail(Number(p.split("/")[4]));
  }

  if (p === "/api/onco/auditoria/resumo") {
    return {
      qt_sem_nota: 1, qt_sem_recebimento: 1, qt_remessa_paga_sem_recebimento: 0,
      qt_receb_maior_faturado: 0, qt_parcialmente_recebida: 2, qt_recebida_com_glosa: 1,
      vl_saldo_financeiro_aberto: 35260, vl_saldo_glosado: 1200,
    };
  }
  if (p === "/api/onco/auditoria/detalhe") return auditDetails;
  if (p === "/api/onco/auditoria/recebimentos/resumo") {
    return {
      qt_contas: 4, qt_recebidas: 1, qt_recebidas_com_glosa: 1,
      qt_parcialmente_recebidas: 1, qt_parcialmente_recebidas_com_glosa: 1,
      qt_multiplos_recebimentos: 1, vl_faturado: 82970, vl_recebido_base_periodo: 66330,
      vl_glosa_periodo: 1200, vl_saldo_total_estimado: 16640,
      vl_saldo_glosado: 1200, vl_saldo_financeiro_aberto: 15440, truncado: false,
    };
  }
  if (p === "/api/onco/auditoria/recebimentos/detalhe") {
    return paymentAccounts.filter((row) => row.status_recebimento !== "RECEBIDA");
  }

  if (p === "/api/onco/glosas/motivos") {
    return [
      { adjustment_reason_code: 1, adjustment_reason_description: "Divergência documental", qt_glosas: 1, qt_contas: 1, vl_glosa: 600, vl_revertida: 0, vl_liquida: 600 },
      { adjustment_reason_code: 2, adjustment_reason_description: "Validação contratual", qt_glosas: 1, qt_contas: 1, vl_glosa: 600, vl_revertida: 0, vl_liquida: 600 },
    ];
  }
  if (p === "/api/onco/glosas") return denials;
  if (p === "/api/onco/produtos") return products;
  if (p === "/api/onco/comparativo") return comparison();

  if (p === "/api/auth/audit-log") {
    return [
      { id: 1, occurred_at: "2026-10-01T12:00:00Z", actor_username: "portfolio", event_type: "LOGIN_OK", details: "Demo session", remote_addr: "127.0.0.1" },
      { id: 2, occurred_at: "2026-10-01T12:05:00Z", actor_username: "portfolio", event_type: "REPORT_VIEWED", details: "Synthetic dataset", remote_addr: "127.0.0.1" },
    ];
  }

  return [];
}

export function demoDownloadUrl(filename, label = "Synthetic portfolio export") {
  if (!DEMO_MODE) return "";
  const body = [
    label,
    "",
    "This file was generated by the public demo mode.",
    "All values displayed by the demo are synthetic and do not represent real patients or institutions.",
  ].join("\n");
  return `data:text/plain;charset=utf-8,${encodeURIComponent(body)}#${encodeURIComponent(filename)}`;
}
