import test from "node:test";
import assert from "node:assert/strict";

import { demoResponse } from "./demoData.js";

test("demo exposes financial capabilities", () => {
  const data = demoResponse("/api/onco/capabilities");

  assert.equal(data.pacientes, true);
  assert.equal(data.recebimento_efetivo, true);
  assert.equal(data.demo, true);
});

test("demo keeps billed, received and open balances distinct", () => {
  const rows = demoResponse("/api/onco/pagamentos/contas?data_inicio=2026-07-01&data_fim=2026-09-30");

  assert.ok(rows.length >= 3);

  const partial = rows.find((row) => row.status_recebimento === "PARCIALMENTE_RECEBIDA_COM_GLOSA");
  assert.ok(partial);
  assert.ok(partial.vl_faturado > partial.vl_recebido_base_acum);
  assert.ok(partial.vl_saldo_glosado > 0);
  assert.ok(partial.vl_saldo_financeiro_aberto > 0);
});

test("demo account drill-down is traceable", () => {
  const detail = demoResponse("/api/onco/contas/81002");

  assert.equal(detail.conta.account_id, 81002);
  assert.ok(detail.itens.length > 0);
  assert.ok(detail.recebimentos.length > 0);
  assert.ok(detail.glosas.length > 0);
});
