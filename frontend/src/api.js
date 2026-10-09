import { DEMO_MODE, demoDownloadUrl, demoResponse } from "./demoData.js";

const API_BASE = import.meta.env.VITE_API_BASE || "";
let currentConvenioId = Number(localStorage.getItem("oncology_payer") || 100);

export function setApiConvenio(cd) {
  currentConvenioId = Number(cd || 100);
}

function qs(inicio, fim, extra = {}) {
  return new URLSearchParams({ data_inicio: inicio, data_fim: fim, ...extra }).toString();
}

async function getJson(path) {
  if (DEMO_MODE) return demoResponse(path);

  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "X-Payer-Id": String(currentConvenioId || 100) },
  });
  const raw = await response.text();
  let payload; let parsed = false;
  if (raw) { try { payload = JSON.parse(raw); parsed = true; } catch { parsed = false; } }
  if (!response.ok) {
    let message = `Erro HTTP ${response.status} ao consultar ${path}`;
    if (parsed && payload) {
      if (typeof payload.detail === "string") message = payload.detail;
      else if (Array.isArray(payload.detail)) message = payload.detail.map((item)=>item?.msg || String(item)).join("; ") || message;
      else if (typeof payload.message === "string") message = payload.message;
    }
    const err = new Error(message); err.status = response.status; throw err;
  }
  if (!raw) return null;
  if (!parsed) throw new Error(`Resposta inválida do servidor ao consultar ${path}`);
  return payload;
}

export const api = {
  capabilities: () => getJson(`/api/onco/capabilities`),
  auditLog: (limit = 200) => getJson(`/api/auth/audit-log?limit=${limit}`),
  resumo: (inicio, fim) => getJson(`/api/onco/resumo?${qs(inicio, fim)}`),
  resumoIntegrado: (inicio, fim, setores = "10") => getJson(`/api/onco/resumo-integrado?${qs(inicio, fim, setores ? { setores } : {})}`),
  financeiro: (inicio, fim) => getJson(`/api/onco/financeiro?${qs(inicio, fim)}`),
  financeiroMensal: (inicio, fim) => getJson(`/api/onco/financeiro/mensal?${qs(inicio, fim)}`),
  faturamentoCompetenciaResumo: (inicio, fim, setores = "") => getJson(`/api/onco/faturamento-competencia/resumo?${qs(inicio, fim, setores ? { setores } : {})}`),
  faturamentoCompetenciaMensal: (inicio, fim, setores = "") => getJson(`/api/onco/faturamento-competencia/mensal?${qs(inicio, fim, setores ? { setores } : {})}`),
  faturamentoCompetenciaSetores: (inicio, fim, setores = "") => getJson(`/api/onco/faturamento-competencia/setores?${qs(inicio, fim, setores ? { setores } : {})}`),
  comparativo: (inicio, fim) => getJson(`/api/onco/comparativo?${qs(inicio, fim)}`),
  pagamentosResumo: (inicio, fim) => getJson(`/api/onco/pagamentos/resumo?${qs(inicio, fim)}`),
  historicoCompetencias: (inicio, fim) => getJson(`/api/onco/historico-competencias?${qs(inicio, fim)}`),
  pagamentosCompetencia: (inicio, fim) => getJson(`/api/onco/pagamentos/competencia?${qs(inicio, fim)}`),
  pagamentosEventos: (inicio, fim, limit = 100) => getJson(`/api/onco/pagamentos/eventos?${qs(inicio, fim, { limit })}`),
  pagamentosContas: (inicio, fim, limit = 100) => getJson(`/api/onco/pagamentos/contas?${qs(inicio, fim, { limit })}`),
  pagamentosAging: (inicio, fim) => getJson(`/api/onco/pagamentos/aging?${qs(inicio, fim)}`),
  pagamentoItens: (evento, limit = 500) => getJson(`/api/onco/pagamentos/eventos/${evento}/itens?limit=${limit}`),
  auditoriaResumo: (inicio, fim) => getJson(`/api/onco/auditoria/resumo?${qs(inicio, fim)}`),
  auditoriaDetalhe: (inicio, fim, limit = 200) => getJson(`/api/onco/auditoria/detalhe?${qs(inicio, fim, { limit })}`),
  auditoriaRecebimentosResumo: (inicio, fim) => getJson(`/api/onco/auditoria/recebimentos/resumo?${qs(inicio, fim)}`),
  auditoriaRecebimentosDetalhe: (inicio, fim, limit = 200) => getJson(`/api/onco/auditoria/recebimentos/detalhe?${qs(inicio, fim, { limit })}`),
  atendimentos: (inicio, fim, limit = 100) => getJson(`/api/onco/atendimentos?${qs(inicio, fim, { limit })}`),
  pacientes: (inicio, fim, limit = 100) => getJson(`/api/onco/pacientes?${qs(inicio, fim, { limit })}`),
  remessas: (inicio, fim, limit = 100) => getJson(`/api/onco/remessas?${qs(inicio, fim, { limit })}`),
  pacienteContas: (paciente, inicio, fim) => getJson(`/api/onco/pacientes/${paciente}/contas?${qs(inicio, fim)}`),
  contaDetalhe: (conta) => getJson(`/api/onco/contas/${conta}`),
  contaPdfUrl: (conta) => DEMO_MODE ? demoDownloadUrl(`conta-${conta}.txt`, "Synthetic account report") : `${API_BASE}/api/onco/contas/${conta}/pdf`,
  glosasMotivos: (inicio, fim) => getJson(`/api/onco/glosas/motivos?${qs(inicio, fim)}`),
  glosas: (inicio, fim, limit = 100) => getJson(`/api/onco/glosas?${qs(inicio, fim, { limit })}`),
  produtos: (inicio, fim, limit = 100) => getJson(`/api/onco/produtos?${qs(inicio, fim, { limit })}`),
  pdfUrl: (inicio, fim, detalhado = false) => DEMO_MODE ? demoDownloadUrl(`oncology-report-${inicio}-${fim}.txt`, detalhado ? "Synthetic detailed report" : "Synthetic executive report") : `${API_BASE}/api/onco/export/pdf?${qs(inicio, fim, { detalhado })}`,
  xmlUrl: (inicio, fim) => DEMO_MODE ? demoDownloadUrl(`oncology-${inicio}-${fim}.txt`, "Synthetic XML export preview") : `${API_BASE}/api/onco/export/xml?${qs(inicio, fim)}`,
  pagamentosCsvUrl: (inicio, fim) => DEMO_MODE ? demoDownloadUrl(`payments-${inicio}-${fim}.txt`, "Synthetic payments export") : `${API_BASE}/api/onco/export/pagamentos.csv?${qs(inicio, fim)}`,
  faturamentoCompetenciaCsvUrl: (inicio, fim, setores = "") => DEMO_MODE ? demoDownloadUrl(`billing-${inicio}-${fim}.txt`, "Synthetic billing export") : `${API_BASE}/api/onco/export/faturamento-competencia.csv?${qs(inicio, fim, setores ? { setores } : {})}`,
  atendimentosCsvUrl: (inicio, fim) => DEMO_MODE ? demoDownloadUrl(`attendances-${inicio}-${fim}.txt`, "Synthetic attendance export") : `${API_BASE}/api/onco/export/atendimentos.csv?${qs(inicio, fim)}`,
  pacientesCsvUrl: (inicio, fim) => DEMO_MODE ? demoDownloadUrl(`patients-${inicio}-${fim}.txt`, "Synthetic patient export") : `${API_BASE}/api/onco/export/pacientes.csv?${qs(inicio, fim)}`,
};
