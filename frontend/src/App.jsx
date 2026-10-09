import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from "recharts";
import { api, setApiConvenio } from "./api";
import { authApi } from "./authApi.js";
import { brl, pct, int } from "./format";

function iso(d) {
  return d.toISOString().slice(0, 10);
}

function defaultRange() {
  const end = new Date();
  const start = new Date(end);
  start.setDate(end.getDate() - 6);
  return [iso(start), iso(end)];
}

function shortDate(value) {
  return value ? String(value).slice(0, 10).split("-").reverse().join("/") : "-";
}

function monthLabel(value) {
  if (!value) return "-";
  const [y, m] = String(value).slice(0, 7).split("-");
  return y && m ? `${m}/${y}` : String(value);
}

function num(value, digits = 1) {
  return Number(value || 0).toLocaleString("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function Card({ title, value, subtitle, tone = "", onClick }) {
  const clickable = typeof onClick === "function";
  return (
    <div
      className={`metric-card ${tone} ${clickable ? "clickable" : ""}`}
      onClick={onClick}
      role={clickable ? "button" : undefined}
      tabIndex={clickable ? 0 : undefined}
      onKeyDown={(e) => clickable && (e.key === "Enter" || e.key === " ") && onClick()}
    >
      <div className="metric-label">{title}</div>
      <div className="metric-value">{value}</div>
      {subtitle && <div className="metric-subtitle">{subtitle}</div>}
    </div>
  );
}

function Section({ title, subtitle, children, actions, id }) {
  return (
    <section className="panel-section" id={id}>
      <div className="section-head">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {actions && <div className="section-actions">{actions}</div>}
      </div>
      {children}
    </section>
  );
}

function StatusBadge({ value }) {
  const text = String(value || "-");
  const upper = text.toUpperCase();
  let tone = "neutral";
  if (upper.includes("RECEBIDA") && !upper.includes("PARCIAL")) tone = "ok";
  if (upper.includes("PAGA") && !upper.includes("SEM") && !upper.includes("NAO")) tone = "ok";
  if (upper.includes("GLOSA") || upper.includes("PARCIAL") || upper.includes("AGUARDANDO")) tone = "warn";
  if (upper.includes("SEM_RECEBIMENTO") || upper.includes("MAIOR") || upper.includes("ESTORNO")) tone = "danger";
  return <span className={`status-badge ${tone}`}>{text.replaceAll("_", " ")}</span>;
}

function DataTable({ columns, rows, keyField, empty = "Nenhum registro encontrado.", onRowClick }) {
  if (!rows?.length) return <div className="empty-state">{empty}</div>;
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr
              key={row[keyField] ?? idx}
              className={onRowClick ? "row-clickable" : ""}
              onClick={() => onRowClick?.(row)}
              tabIndex={onRowClick ? 0 : undefined}
              onKeyDown={(e) => onRowClick && (e.key === "Enter" || e.key === " ") && onRowClick(row)}
            >
              {columns.map((c) => (
                <td key={c.key} data-label={c.label} className={c.className || ""}>
                  {c.render ? c.render(row[c.key], row) : row[c.key] ?? "-"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ScopeNote({ children }) {
  return <div className="scope-note">{children}</div>;
}

function SubTabs({ value, onChange, items }) {
  return (
    <div className="subtabs" role="tablist" aria-label="Detalhes da área">
      {items.map(([id, label]) => (
        <button
          key={id}
          type="button"
          className={value === id ? "active" : ""}
          onClick={() => onChange(id)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

function ScopeCard({ title, field, children }) {
  return (
    <div className="scope-card">
      <div className="scope-card-title">{title}</div>
      <code>{field}</code>
      <p>{children}</p>
    </div>
  );
}

function JourneyStep({ step, title, value, state, detail, dateLabel, tone = "neutral", onClick }) {
  const clickable = typeof onClick === "function";
  return (
    <button
      type="button"
      className={`journey-step ${tone} ${clickable ? "clickable" : ""}`}
      onClick={onClick}
      disabled={!clickable}
    >
      <div className="journey-step-head">
        <span className="journey-number">{step}</span>
        <span className="journey-title">{title}</span>
      </div>
      {state ? <div className="journey-state">{state}</div> : <div className="journey-value">{value}</div>}
      {state && value ? <div className="journey-zero-value">{value}</div> : null}
      <div className="journey-detail">{detail}</div>
      <div className="journey-date">{dateLabel}</div>
    </button>
  );
}

function ReceiptMatrix({ rows }) {
  const months = rows.months || [];
  const competences = rows.competences || [];
  if (!months.length || !competences.length) return <div className="empty-state">Sem dados para a matriz.</div>;
  const max = Math.max(1, ...competences.flatMap((r) => months.map((m) => Number(r.values[m] || 0))));
  return (
    <div className="matrix-wrap" role="region" aria-label="Matriz competência por mês de recebimento" tabIndex="0">
      <table className="receipt-matrix">
        <thead><tr><th>Competência</th>{months.map((m) => <th key={m}>{monthLabel(m)}</th>)}</tr></thead>
        <tbody>
          {competences.map((row) => (
            <tr key={row.competencia}>
              <th>{monthLabel(row.competencia)}</th>
              {months.map((m) => {
                const value = Number(row.values[m] || 0);
                const strength = value ? 0.10 + (value / max) * 0.55 : 0;
                return <td key={m} className={value ? "matrix-value" : "matrix-empty"} style={value ? { backgroundColor: `rgba(182, 148, 85, ${strength})` } : undefined}>{value ? brl(value) : "—"}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


function AdminUsers({ convenios = [], sessionUser = null }) {
  const emptyForm = { id:null, username:"", display_name:"", email:"", password:"", role:"VISUALIZACAO", all_convenios:false, convenios:[11], default_convenio:11, must_change_password:true, active:true };
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(emptyForm);
  const [adminView, setAdminView] = useState("users");
  const [editorOpen, setEditorOpen] = useState(false);
  const [auditLog, setAuditLog] = useState([]);
  const [userSearch, setUserSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [convenioFilter, setConvenioFilter] = useState("ALL");
  const [convenioSearch, setConvenioSearch] = useState("");

  async function refresh() {
    setLoading(true); setError("");
    try { setUsers(await authApi.users()); } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }
  useEffect(()=>{ refresh(); }, []);

  function resetForm() { setForm(emptyForm); setNotice(""); setError(""); setEditorOpen(false); setConvenioSearch(""); }
  function edit(user) {
    setAdminView("users");
    setForm({
      id:user.id,
      username:user.username || "",
      display_name:user.display_name || "",
      email:user.email || "",
      password:"",
      role:user.role || "VISUALIZACAO",
      all_convenios:Boolean(user.all_convenios),
      convenios:user.convenios?.length ? user.convenios : [11],
      default_convenio:Number(user.default_convenio || user.convenios?.[0] || 11),
      must_change_password:Boolean(user.must_change_password),
      active:Boolean(user.active),
    });
    setEditorOpen(true);
    setNotice(""); setError(""); setConvenioSearch("");
  }

  function toggleConvenio(cd) {
    const id = Number(cd);
    const has = form.convenios.includes(id);
    const next = has ? form.convenios.filter(x=>x!==id) : [...form.convenios,id].sort((a,b)=>a-b);
    const nextDefault = next.includes(form.default_convenio) ? form.default_convenio : (next[0] || null);
    setForm({...form, convenios: next, default_convenio: nextDefault});
  }

  async function save(e) {
    e.preventDefault(); setError(""); setNotice("");
    try {
      if (!form.all_convenios && !form.convenios.length) throw new Error("Selecione ao menos um convênio ou libere todos os convênios.");
      if (!form.all_convenios && form.default_convenio && !form.convenios.includes(Number(form.default_convenio))) throw new Error("O convênio padrão precisa estar entre os convênios autorizados.");
      if (form.id) {
        const payload = {
          display_name:form.display_name, email:form.email, role:form.role, active:form.active,
          all_convenios:form.all_convenios, convenios:form.all_convenios ? [] : form.convenios,
          default_convenio:form.default_convenio || null, must_change_password:form.must_change_password,
        };
        if (form.password) payload.password = form.password;
        await authApi.updateUser(form.id, payload);
        setNotice("Usuário atualizado com sucesso.");
      } else {
        await authApi.createUser({
          username:form.username, display_name:form.display_name, email:form.email, password:form.password,
          role:form.role, all_convenios:form.all_convenios, convenios:form.all_convenios ? [] : form.convenios,
          default_convenio:form.default_convenio || null, must_change_password:form.must_change_password,
        });
        setNotice("Usuário criado com sucesso.");
      }
      await refresh();
      setEditorOpen(false);
      setForm(emptyForm);
    } catch (e) { setError(e.message); }
  }

  async function toggle(user) {
    setError(""); setNotice("");
    const action = user.active ? "bloquear" : "reativar";
    if (user.active && !window.confirm(`Confirma bloquear o acesso de ${user.display_name || user.username}?`)) return;
    try {
      await authApi.updateUser(user.id, { active: !user.active });
      await refresh();
      setNotice(action === "bloquear" ? "Usuário bloqueado." : "Usuário reativado.");
    } catch (e) { setError(e.message); }
  }

  const roleInfo = [
    ["ADMIN", "Administrador", "Acesso completo, gestão de usuários, convênios, relatórios e configurações."],
    ["FATURAMENTO", "Faturamento", "Contas, faturamento MV, recebimentos, glosas, pendências e relatórios."],
    ["AUDITORIA", "Auditoria", "Leitura operacional completa, rastreabilidade e exportações; sem gestão de usuários."],
    ["VISUALIZACAO", "Visualização", "Resumo executivo e análises agregadas dos convênios autorizados."],
  ];

  const filteredUsers = users.filter((user) => {
    const hay = `${user.display_name||""} ${user.username||""} ${user.email||""}`.toLowerCase();
    if (userSearch && !hay.includes(userSearch.toLowerCase())) return false;
    if (roleFilter !== "ALL" && user.role !== roleFilter) return false;
    if (statusFilter === "ACTIVE" && !user.active) return false;
    if (statusFilter === "BLOCKED" && user.active) return false;
    if (convenioFilter !== "ALL") {
      const cd = Number(convenioFilter);
      if (!user.all_convenios && !(user.convenios||[]).includes(cd)) return false;
    }
    return true;
  });

  const filteredConvenios = convenios.filter(c => `${c.nm_convenio} ${c.cd_convenio}`.toLowerCase().includes(convenioSearch.toLowerCase()));
  const allowedForDefault = form.all_convenios ? convenios : convenios.filter(c=>form.convenios.includes(c.cd_convenio));

  return <>
    <div className="admin-header">
      <div><span className="admin-kicker">ADMINISTRAÇÃO</span><h2>Governança de acesso</h2><p>Usuários, perfis e convênios autorizados em um único lugar.</p></div>
      <button className="primary-action" type="button" onClick={()=>{setForm(emptyForm);setNotice("");setError("");setAdminView("users");setEditorOpen(true)}}>+ Novo usuário</button>
    </div>
    <SubTabs value={adminView} onChange={setAdminView} items={[["users","Usuários e acessos"],["profiles","Perfis e permissões"],["convenios","Convênios disponíveis"],["audit","Log de acessos"]]} />

    {error && <div className="error">{error}</div>}
    {notice && <div className="success-note">{notice}</div>}

    {adminView === "profiles" && <div className="access-role-grid">
      {roleInfo.map(([id,title,desc])=><div className={`role-card role-${id.toLowerCase()}`} key={id}><span className="role-code">{id}</span><strong>{title}</strong><span>{desc}</span></div>)}
    </div>}

    {adminView === "convenios" && <Section title="Convênios disponíveis" subtitle="O usuário só enxerga convênios liberados em seu cadastro. Indicadores assistenciais/financeiros exigem modelo homologado por convênio.">
      <div className="convenio-admin-grid">{convenios.map(c=><div className="convenio-admin-card" key={c.cd_convenio}><strong>{c.nm_convenio}</strong><span>Convênio {c.cd_convenio}</span><StatusBadge value={c.modelo_homologado ? "MODELO HOMOLOGADO" : "AGUARDANDO HOMOLOGAÇÃO"}/></div>)}</div>
    </Section>}

    {adminView === "audit" && <Section title="Log de acessos" subtitle="Rastreabilidade de login, logout, troca de senha e alterações de usuários.">
      <div className="admin-audit-actions"><button className="secondary-button" type="button" onClick={async()=>{try{setAuditLog(await authApi.auditLog(200));}catch(e){setError(e.message)}}}>Atualizar log</button></div>
      {auditLog.length === 0 ? <div className="empty-state">Clique em “Atualizar log” para carregar os eventos.</div> : <DataTable keyField="id" rows={auditLog} columns={[
        {key:"occurred_at",label:"Data/hora",render:(v)=>v?new Date(v).toLocaleString("pt-BR"):"—"},
        {key:"actor_username",label:"Usuário"},{key:"event_type",label:"Evento"},{key:"target_user_id",label:"Alvo"},{key:"remote_addr",label:"Origem"},{key:"details",label:"Detalhes"}
      ]}/>} 
    </Section>}

    {adminView === "users" && <>
      <Section title="Usuários cadastrados" subtitle={`${filteredUsers.length} de ${users.length} usuário(s) exibido(s). Edite permissões e status sem apagar o histórico.`}>
        <div className="admin-filterbar">
          <input className="search" placeholder="Buscar nome, usuário ou e-mail" value={userSearch} onChange={e=>setUserSearch(e.target.value)}/>
          <select value={roleFilter} onChange={e=>setRoleFilter(e.target.value)}><option value="ALL">Todos os perfis</option><option value="ADMIN">Administrador</option><option value="FATURAMENTO">Faturamento</option><option value="AUDITORIA">Auditoria</option><option value="VISUALIZACAO">Visualização</option></select>
          <select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}><option value="ALL">Todos os status</option><option value="ACTIVE">Ativos</option><option value="BLOCKED">Bloqueados</option></select>
          <select value={convenioFilter} onChange={e=>setConvenioFilter(e.target.value)}><option value="ALL">Todos os convênios</option>{convenios.map(c=><option key={c.cd_convenio} value={c.cd_convenio}>{c.nm_convenio}</option>)}</select>
        </div>
        {loading ? <div className="empty-state">Carregando usuários…</div> : filteredUsers.length ? <div className="admin-users-list">
          {filteredUsers.map(user=><div className="admin-user-row" key={user.id}>
            <div className="admin-avatar">{String(user.display_name||user.username||"U").trim().split(/\s+/).slice(0,2).map(x=>x[0]).join("").toUpperCase()}</div>
            <div className="admin-user-main"><strong>{user.display_name}</strong><span>{user.username}{user.email ? ` · ${user.email}` : ""}</span></div>
            <StatusBadge value={user.role}/>
            <div className="admin-convenios"><strong>{user.all_convenios ? "Todos os convênios" : `${(user.convenios||[]).length} autorizado(s)`}</strong><span>{user.all_convenios ? "Acesso global" : (user.convenios||[]).map(cd=>convenios.find(c=>c.cd_convenio===cd)?.nm_convenio || cd).join(", ") || "Nenhum"}</span></div>
            <span className={`access-status ${user.active?"active":"blocked"}`}>{user.active?"Ativo":"Bloqueado"}</span>
            <div className="admin-user-actions"><button className="mini-action" type="button" onClick={()=>edit(user)}>Editar</button><button className="mini-action" type="button" disabled={user.active && sessionUser?.id===user.id} title={user.active && sessionUser?.id===user.id ? "Para sua segurança, bloqueie sua conta usando outro administrador." : ""} onClick={()=>toggle(user)}>{user.active?"Bloquear":"Reativar"}</button></div>
          </div>)}
        </div> : <div className="empty-state">Nenhum usuário corresponde aos filtros.</div>}
      </Section>

      {editorOpen && <div className="modal-backdrop" role="presentation" onMouseDown={(e)=>{if(e.target===e.currentTarget)resetForm()}}><div className="admin-modal" role="dialog" aria-modal="true" aria-label={form.id ? "Editar usuário" : "Novo usuário"}>
        <div className="modal-head"><div><span className="admin-kicker">ADMINISTRAÇÃO</span><h2>{form.id ? "Editar usuário" : "Novo usuário"}</h2><p>Perfil, convênio padrão e permissões são controlados pela aplicação. O Oracle permanece read-only.</p></div><button type="button" className="modal-close" onClick={resetForm}>×</button></div>
        <form className="user-form v61-user-form" onSubmit={save}>
          <label>Nome completo<input required value={form.display_name} onChange={e=>setForm({...form,display_name:e.target.value})}/></label>
          <label>Usuário<input required minLength="3" disabled={Boolean(form.id)} value={form.username} onChange={e=>setForm({...form,username:e.target.value})}/></label>
          <label>E-mail<input type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label>
          <label>{form.id ? "Redefinir senha (opcional)" : "Senha inicial"}<input required={!form.id} type="password" minLength={form.id?0:12} value={form.password} onChange={e=>setForm({...form,password:e.target.value})} placeholder={form.id?"deixe vazio para manter":"mínimo 12 caracteres"}/></label>
          <label>Perfil<select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option value="ADMIN">Administrador</option><option value="FATURAMENTO">Faturamento</option><option value="AUDITORIA">Auditoria</option><option value="VISUALIZACAO">Visualização</option></select></label>
          <label>Convênio padrão<select value={form.default_convenio || ""} onChange={e=>setForm({...form,default_convenio:Number(e.target.value)})}><option value="">Selecione</option>{allowedForDefault.map(c=><option key={c.cd_convenio} value={c.cd_convenio}>{c.nm_convenio} · Convênio {c.cd_convenio}</option>)}</select></label>
          {form.id && <label>Status<select value={form.active?"1":"0"} onChange={e=>setForm({...form,active:e.target.value==="1"})}><option value="1">Ativo</option><option value="0">Bloqueado</option></select></label>}
          <div className="convenio-permission-box">
            <div className="permission-toolbar"><label className="check-field"><input type="checkbox" checked={form.all_convenios} onChange={e=>setForm({...form,all_convenios:e.target.checked})}/> <strong>Acesso a todos os convênios</strong></label><label className="check-field"><input type="checkbox" checked={form.must_change_password} onChange={e=>setForm({...form,must_change_password:e.target.checked})}/> <strong>Exigir troca de senha no próximo acesso</strong></label></div>
            {!form.all_convenios && <>
              <div className="convenio-picker-head"><div><strong>Convênios autorizados</strong><span>{form.convenios.length} selecionado(s)</span></div><input className="search" value={convenioSearch} onChange={e=>setConvenioSearch(e.target.value)} placeholder="Buscar convênio ou código"/></div>
              <div className="convenio-check-scroll"><div className="convenio-check-grid">{filteredConvenios.map(c=><label className="convenio-check" key={c.cd_convenio}><input type="checkbox" checked={form.convenios.includes(c.cd_convenio)} onChange={()=>toggleConvenio(c.cd_convenio)}/><span><strong>{c.nm_convenio}</strong><small>Convênio {c.cd_convenio}{c.modelo_homologado?" · homologado":""}</small></span></label>)}</div>{filteredConvenios.length===0 && <div className="empty-state compact">Nenhum convênio encontrado.</div>}</div>
            </>}
          </div>
          <div className="user-form-actions"><button className="primary-action" type="submit">{form.id ? "Salvar alterações" : "Criar usuário"}</button><button className="secondary-button" type="button" onClick={resetForm}>Cancelar</button></div>
        </form>
      </div></div>}
    </>}
  </>;
}

const TABS = [
  ["resumo", "Resumo integrado"],
  ["contas", "Contas e pacientes"],
  ["recebimentos", "Recebimentos"],
  ["pendencias", "Glosas e pendências"],
  ["analises", "Análises"],
  ["relatorios", "Relatórios"],
];

export default function App({ session, convenios = [], convenio, onConvenioChange, onLogout }) {
  const [initialStart, initialEnd] = useMemo(defaultRange, []);
  const [inicio, setInicio] = useState(initialStart);
  const [fim, setFim] = useState(initialEnd);
  const [applied, setApplied] = useState([initialStart, initialEnd]);
  const [tab, setTab] = useState("resumo");
  const [contasView, setContasView] = useState("atendimentos");
  const [pendenciasView, setPendenciasView] = useState("auditoria");
  const [analisesView, setAnalisesView] = useState("faturamentoMv");

  const [resumo, setResumo] = useState({});
  const [financeiro, setFinanceiro] = useState({});
  const [capabilities, setCapabilities] = useState({});
  const [mensal, setMensal] = useState([]);
  const [fatMvResumo, setFatMvResumo] = useState({});
  const [fatMvMensal, setFatMvMensal] = useState([]);
  const [fatMvSetores, setFatMvSetores] = useState([]);
  const [integrado, setIntegrado] = useState({});
  const [setoresMv, setSetoresMv] = useState("113");
  const [atendimentos, setAtendimentos] = useState([]);
  const [pacientes, setPacientes] = useState([]);
  const [motivos, setMotivos] = useState([]);
  const [glosas, setGlosas] = useState([]);
  const [produtos, setProdutos] = useState([]);

  const [pagResumo, setPagResumo] = useState({});
  const [pagCompetencia, setPagCompetencia] = useState([]);
  const [historicoCompetencias, setHistoricoCompetencias] = useState([]);
  const [pagAging, setPagAging] = useState({});
  const [pagEventos, setPagEventos] = useState([]);
  const [pagContas, setPagContas] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [eventItems, setEventItems] = useState([]);

  const [audResumo, setAudResumo] = useState({});
  const [audDetalhe, setAudDetalhe] = useState([]);
  const [audRecResumo, setAudRecResumo] = useState({});
  const [audRecDetalhe, setAudRecDetalhe] = useState([]);
  const [comparativo, setComparativo] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientAccounts, setPatientAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [accountDetail, setAccountDetail] = useState(null);

  const [search, setSearch] = useState("");
  const [privacy, setPrivacy] = useState(false);
  const [loadingBase, setLoadingBase] = useState(false);
  const [loading, setLoading] = useState({});
  const [erro, setErro] = useState("");
  const [loaded, setLoaded] = useState({});

  const [fInicio, fFim] = applied;
  const convenioSupported = convenio ? Boolean(convenio.modelo_homologado) : true;
  const role = String(session?.user?.role || "VISUALIZACAO");
  const tabs = role === "ADMIN" ? [...TABS, ["admin", "Administração"]]
    : role === "VISUALIZACAO" ? TABS.filter(([id]) => ["resumo","analises"].includes(id))
    : TABS;

  useEffect(() => {
    if (convenio?.cd_convenio) setApiConvenio(convenio.cd_convenio);
  }, [convenio?.cd_convenio]);

  async function loadBase() {
    if (!convenioSupported) return;
    setLoadingBase(true);
    setErro("");
    try {
      const caps = await api.capabilities();
      setCapabilities(caps || {});
      const r = await api.resumo(fInicio, fFim);
      setResumo(r || {});
      const f = await api.financeiro(fInicio, fFim);
      setFinanceiro(f || {});
    } catch (e) {
      setErro(e.message || "Falha ao carregar dados.");
    } finally {
      setLoadingBase(false);
    }
  }

  useEffect(() => {
    setResumo({});
    setFinanceiro({});
    setMensal([]);
    setFatMvResumo({});
    setFatMvMensal([]);
    setFatMvSetores([]);
    setIntegrado({});
    setAtendimentos([]);
    setPacientes([]);
    setMotivos([]);
    setGlosas([]);
    setProdutos([]);
    setPagResumo({});
    setPagCompetencia([]);
    setHistoricoCompetencias([]);
    setPagAging({});
    setPagEventos([]);
    setPagContas([]);
    setSelectedEvent(null);
    setEventItems([]);
    setAudResumo({});
    setAudDetalhe([]);
    setAudRecResumo({});
    setAudRecDetalhe([]);
    setComparativo(null);
    setSelectedPatient(null);
    setPatientAccounts([]);
    setSelectedAccount(null);
    setAccountDetail(null);
    setLoaded({});
    setSearch("");
    if (convenioSupported) loadBase();
  }, [fInicio, fFim, convenio?.cd_convenio, convenioSupported]);

  async function runLazy(name, fn, setter) {
    if (loaded[name] || loading[name]) return;
    setLoading((s) => ({ ...s, [name]: true }));
    setErro("");
    try {
      setter(await fn());
      setLoaded((s) => ({ ...s, [name]: true }));
    } catch (e) {
      setErro(e.message || "Falha ao consultar dados.");
    } finally {
      setLoading((s) => ({ ...s, [name]: false }));
    }
  }

  async function loadIntegrated() {
    if (loaded.integrated || loading.integrated) return;
    setLoading((s) => ({ ...s, integrated: true }));
    setErro("");
    try {
      const r = await api.resumoIntegrado(fInicio, fFim, "113");
      setIntegrado(r || {});
      setLoaded((s) => ({ ...s, integrated: true }));
    } catch (e) {
      setErro(e.message || "Falha ao montar o resumo integrado.");
    } finally {
      setLoading((s) => ({ ...s, integrated: false }));
    }
  }

  async function loadFaturamentoMv() {
    if (loading.faturamentoMv) return;
    setLoading((s) => ({ ...s, faturamentoMv: true }));
    setErro("");
    try {
      const filtroSetores = setoresMv.trim();
      // Sequencial por desenho: reproduz a regra nativa sem abrir várias consultas pesadas em paralelo.
      const r = await api.faturamentoMvResumo(fInicio, fFim, filtroSetores);
      setFatMvResumo(r || {});
      const m = await api.faturamentoMvMensal(fInicio, fFim, filtroSetores);
      setFatMvMensal(m || []);
      const st = await api.faturamentoMvSetores(fInicio, fFim, filtroSetores);
      setFatMvSetores(st || []);
      setLoaded((s) => ({ ...s, faturamentoMv: filtroSetores || "TODOS" }));
    } catch (e) {
      setErro(e.message || "Falha ao consultar faturamento por competência MV.");
    } finally {
      setLoading((s) => ({ ...s, faturamentoMv: false }));
    }
  }

  async function loadPaymentsCore() {
    if (loaded.paymentsCore || loading.paymentsCore) return;
    setLoading((s) => ({ ...s, paymentsCore: true }));
    setErro("");
    try {
      // Sequencial por desenho: evita pico simultâneo no Oracle.
      const r = await api.pagamentosResumo(fInicio, fFim);
      setPagResumo(r || {});
      const a = await api.pagamentosAging(fInicio, fFim);
      setPagAging(a || {});
      const c = await api.pagamentosCompetencia(fInicio, fFim);
      setPagCompetencia(c || []);
      setLoaded((s) => ({ ...s, paymentsCore: true }));
    } catch (e) {
      setErro(e.message || "Falha ao consultar recebimentos.");
    } finally {
      setLoading((s) => ({ ...s, paymentsCore: false }));
    }
  }

  useEffect(() => {
    if (tab === "resumo" && !loaded.integrated && Object.keys(financeiro).length) loadIntegrated();
    if (tab === "recebimentos" || (tab === "pendencias" && pendenciasView === "glosas"))
      loadPaymentsCore();

    if (tab === "contas" && contasView === "atendimentos")
      runLazy("atendimentos", () => api.atendimentos(fInicio, fFim, 500), setAtendimentos);
    if (tab === "contas" && contasView === "pacientes")
      runLazy("pacientes", () => api.pacientes(fInicio, fFim, 500), setPacientes);

    if (tab === "pendencias" && pendenciasView === "auditoria")
      runLazy("audResumo", () => api.auditoriaResumo(fInicio, fFim), setAudResumo);
    if (tab === "pendencias" && pendenciasView === "glosas") {
      runLazy("historicoCompetencias", () => api.historicoCompetencias(fInicio, fFim), setHistoricoCompetencias);
      runLazy("motivos", () => api.glosasMotivos(fInicio, fFim), setMotivos);
      runLazy("glosas", () => api.glosas(fInicio, fFim, 250), setGlosas);
    }

    if (tab === "analises" && analisesView === "faturamentoMv" && !loaded.faturamentoMv) loadFaturamentoMv();
    if (tab === "analises" && analisesView === "producao")
      runLazy("mensal", () => api.financeiroMensal(fInicio, fFim), setMensal);
    if (tab === "analises" && analisesView === "produtos")
      runLazy("produtos", () => api.produtos(fInicio, fFim, 250), setProdutos);
  }, [tab, contasView, pendenciasView, analisesView, fInicio, fFim, financeiro]);

  function aplicar(e) {
    e.preventDefault();
    if (!inicio || !fim) return;
    const d1 = new Date(`${inicio}T00:00:00`);
    const d2 = new Date(`${fim}T00:00:00`);
    const days = Math.floor((d2 - d1) / 86400000) + 1;
    if (days < 1) return setErro("A data final não pode ser anterior à data inicial.");
    if (days > Number(capabilities.periodo_maximo_dias || 365)) return setErro(`Por segurança, selecione no máximo ${capabilities.periodo_maximo_dias || 365} dias por consulta.`);
    setApplied([inicio, fim]);
  }

  const patientName = (value, row) => privacy ? `Paciente ${row?.cd_paciente ?? "restrito"}` : (value || "-");

  const filterRows = (rows, fields) => {
    const q = search.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => fields.some((f) => String(r[f] ?? "").toLowerCase().includes(q)));
  };

  const competenciaTimeline = useMemo(() => {
    const map = new Map();

    for (const row of pagCompetencia) {
      const competencia = row.competencia || "Sem competência";
      const mes = row.mes_recebimento || "Sem mês";

      if (!map.has(competencia)) {
        map.set(competencia, {
          competencia,
          recebido: 0,
          glosa: 0,
          meses: new Map(),
        });
      }

      const item = map.get(competencia);
      const recebido = Number(row.vl_recebido_financeiro || 0);
      const glosa = Number(row.vl_glosa || 0);

      item.recebido += recebido;
      item.glosa += glosa;

      if (!item.meses.has(mes)) {
        item.meses.set(mes, { mes, recebido: 0, glosa: 0 });
      }

      const evento = item.meses.get(mes);
      evento.recebido += recebido;
      evento.glosa += glosa;
    }

    return Array.from(map.values())
      .map((item) => ({
        ...item,
        meses: Array.from(item.meses.values()).sort((a, b) =>
          String(a.mes).localeCompare(String(b.mes))
        ),
      }))
      .sort((a, b) =>
        String(b.competencia).localeCompare(String(a.competencia))
      );
  }, [pagCompetencia]);

  const origemRecebimentos = useMemo(() => {
    const map = new Map();
    for (const row of pagCompetencia) {
      const k = row.competencia || "Sem competência";
      map.set(k, (map.get(k) || 0) + Number(row.vl_recebido_financeiro || 0));
    }
    return [...map.entries()]
      .map(([competencia, valor]) => ({ competencia: monthLabel(competencia), valor }))
      .sort((a, b) => a.competencia.localeCompare(b.competencia));
  }, [pagCompetencia]);

  const receiptMatrix = useMemo(() => {
    const months = [...new Set(pagCompetencia.map((r) => r.mes_recebimento).filter(Boolean))].sort();
    const compKeys = [...new Set(pagCompetencia.map((r) => r.competencia).filter(Boolean))].sort();
    const values = new Map();
    for (const row of pagCompetencia) {
      const key = `${row.competencia}|${row.mes_recebimento}`;
      values.set(key, (values.get(key) || 0) + Number(row.vl_recebido_financeiro || 0));
    }
    return {
      months,
      competences: compKeys.map((competencia) => ({
        competencia,
        values: Object.fromEntries(months.map((m) => [m, values.get(`${competencia}|${m}`) || 0])),
      })),
    };
  }, [pagCompetencia]);

  async function abrirEvento(row) {
    const id = row.cd_reccon_rec;
    setSelectedEvent(row);
    setEventItems([]);
    setLoading((s) => ({ ...s, eventItems: true }));
    setErro("");
    try {
      setEventItems(await api.pagamentoItens(id, 1000));
    } catch (e) {
      setErro(e.message || "Falha ao abrir evento financeiro.");
    } finally {
      setLoading((s) => ({ ...s, eventItems: false }));
    }
  }

  async function abrirPaciente(row) {
    setSelectedPatient(row);
    setPatientAccounts([]);
    setLoading((v) => ({ ...v, patientAccounts: true }));
    setErro("");
    try {
      const rows = await api.pacienteContas(row.cd_paciente, fInicio, fFim);
      setPatientAccounts(rows || []);
    } catch (e) {
      setErro(e.message || "Falha ao abrir o paciente.");
    } finally {
      setLoading((v) => ({ ...v, patientAccounts: false }));
    }
  }

  async function abrirConta(row) {
    const id = row?.cd_reg_amb;
    if (!id) return;
    setSelectedAccount(row);
    setAccountDetail(null);
    setLoading((v) => ({ ...v, accountDetail: true }));
    setErro("");
    try {
      setAccountDetail(await api.contaDetalhe(id));
    } catch (e) {
      setErro(e.message || "Falha ao abrir a conta.");
    } finally {
      setLoading((v) => ({ ...v, accountDetail: false }));
    }
  }

  const itemCols = [
    { key: "cd_lancamento", label: "Lançamento" },
    { key: "dt_sessao", label: "Sessão", render: (v, r) => shortDate(v || r.dt_producao) },
    { key: "cd_pro_fat", label: "Código" },
    { key: "ds_pro_fat", label: "Descrição do item" },
    { key: "qt_lancamento", label: "Qtde", render: (v) => num(v, 2), className: "number" },
    { key: "vl_unitario", label: "Valor unit.", render: brl, className: "number" },
    { key: "vl_total_conta", label: "Valor total", render: brl, className: "number" },
    { key: "cd_guia", label: "Guia" },
  ];

  const atendCols = [
    { key: "nm_paciente", label: "Paciente", render: patientName },
    { key: "cd_atendimento", label: "Atendimento" },
    { key: "cd_reg_amb", label: "Conta" },
    { key: "dt_atendimento", label: "Data", render: shortDate },
    { key: "cd_remessa", label: "Remessa" },
    { key: "status_financeiro", label: "Status", render: (v) => <StatusBadge value={v} /> },
    { key: "vl_faturado", label: "Faturado", render: brl, className: "number" },
    { key: "vl_recebido_base", label: "Recebido base", render: brl, className: "number" },
    { key: "vl_acrescimo_recebimento", label: "Acréscimos", render: brl, className: "number" },
    { key: "vl_saldo_estimado", label: "Saldo", render: brl, className: "number" },
    { key: "ultimo_recebimento", label: "Último receb.", render: shortDate },
    { key: "vl_glosa_liquida", label: "Glosa", render: brl, className: "number" },
    ...(capabilities.custo_medicamento ? [{ key: "vl_custo_medicamento", label: "Custo medicamento*", render: brl, className: "number" }] : []),
  ];

  const pacCols = [
    { key: "nm_paciente", label: "Paciente", render: patientName },
    { key: "qt_atendimentos", label: "Atend.", render: int, className: "number" },
    { key: "qt_contas", label: "Contas", render: int, className: "number" },
    { key: "vl_faturado", label: "Faturado", render: brl, className: "number" },
    { key: "vl_recebido_base", label: "Recebido base", render: brl, className: "number" },
    { key: "vl_acrescimo_recebimento", label: "Acréscimos", render: brl, className: "number" },
    { key: "vl_saldo_estimado", label: "Saldo", render: brl, className: "number" },
    { key: "vl_glosa_liquida", label: "Glosa", render: brl, className: "number" },
    { key: "vl_medio_por_atendimento", label: "Faturado/atend.", render: brl, className: "number" },
    { key: "vl_recebido_medio_atendimento", label: "Recebido/atend.", render: brl, className: "number" },
    ...(capabilities.custo_medicamento ? [{ key: "vl_custo_medicamento", label: "Custo medicamento*", render: brl, className: "number" }] : []),
  ];

  const eventCols = [
    { key: "cd_reccon_rec", label: "Evento" },
    { key: "dt_recebimento", label: "Recebimento", render: shortDate },
    { key: "qt_remessas_onco", label: "Remessas", render: int, className: "number" },
    { key: "qt_contas_onco", label: "Contas", render: int, className: "number" },
    { key: "qt_pacientes_onco", label: "Pacientes", render: int, className: "number" },
    { key: "vl_evento_total", label: "Evento total", render: brl, className: "number" },
    { key: "vl_onco_recebido", label: "Parcela onco", render: brl, className: "number" },
    { key: "vl_onco_acrescimo", label: "Acréscimos onco", render: brl, className: "number" },
    { key: "pct_onco_evento", label: "% onco", render: pct, className: "number" },
  ];

  const paymentAccountCols = [
    { key: "nm_paciente", label: "Paciente", render: patientName },
    { key: "cd_atendimento", label: "Atendimento" },
    { key: "cd_reg_amb", label: "Conta" },
    { key: "cd_remessa", label: "Remessa" },
    { key: "dt_competencia", label: "Competência", render: (v) => monthLabel(String(v || "").slice(0, 7)) },
    { key: "ultimo_recebimento_no_periodo", label: "Recebido em", render: shortDate },
    { key: "vl_faturado", label: "Faturado", render: brl, className: "number" },
    { key: "vl_recebido_financeiro_periodo", label: "Receb. no período", render: brl, className: "number" },
    { key: "vl_recebido_base_acum", label: "Base acumulada", render: brl, className: "number" },
    { key: "vl_glosa_acum", label: "Glosa acumulada", render: brl, className: "number" },
    { key: "vl_saldo_financeiro_aberto", label: "Saldo aberto", render: brl, className: "number" },
    { key: "vl_saldo_glosado", label: "Saldo glosado", render: brl, className: "number" },
    { key: "status_recebimento", label: "Status", render: (v) => <StatusBadge value={v} /> },
    { key: "dias_atendimento_recebimento", label: "Dias", render: (v) => int(v), className: "number" },
  ];

  const eventItemCols = [
    { key: "nm_paciente", label: "Paciente", render: patientName },
    { key: "cd_atendimento", label: "Atendimento" },
    { key: "cd_reg_amb", label: "Conta" },
    { key: "cd_remessa", label: "Remessa" },
    { key: "cd_itfat_nf", label: "Item NF" },
    { key: "dt_competencia", label: "Competência", render: (v) => monthLabel(String(v || "").slice(0, 7)) },
    { key: "vl_faturado", label: "Faturado item", render: brl, className: "number" },
    { key: "vl_recebido_financeiro", label: "Recebido", render: brl, className: "number" },
    { key: "vl_acrescimo", label: "Acréscimo", render: brl, className: "number" },
    { key: "vl_glosa_recebimento", label: "Glosa", render: brl, className: "number" },
  ];

  const producaoValor = Number(integrado.producao?.valor_contas || 0);
  const faturadoMvValor = Number(integrado.faturamento_mv?.valor || 0);
  const recebidoBaseValor = Number(integrado.recebimentos?.recebido_base || 0);
  const glosaRecebimentoValor = Number(integrado.recebimentos?.glosa_no_recebimento || 0);
  const saldoFinanceiroValor = Number(integrado.pendencias_recebimentos?.saldo_financeiro_aberto || 0);
  const saldoGlosadoValor = Number(integrado.pendencias_recebimentos?.saldo_glosado || 0);
  const totalPendenciasRecebidas = saldoFinanceiroValor + saldoGlosadoValor;

  const executiveSentence = (() => {
    const parts = [];
    if (producaoValor > 0) parts.push(`A oncologia produziu ${brl(producaoValor)} no período selecionado.`);
    else parts.push("Não houve produção oncológica identificada no período selecionado.");

    if (faturadoMvValor > 0) parts.push(`A competência MV somou ${brl(faturadoMvValor)} em faturamento oficial.`);
    else parts.push("Ainda não há faturamento MV fechado na competência selecionada.");

    if (recebidoBaseValor > 0) parts.push(`O financeiro registrou ${brl(recebidoBaseValor)} em recebimentos no intervalo.`);
    else parts.push("Não houve recebimentos financeiros registrados no intervalo.");

    if (totalPendenciasRecebidas > 0) {
      parts.push(`Nas contas recebidas, há ${brl(saldoFinanceiroValor)} em saldo financeiro aberto e ${brl(saldoGlosadoValor)} em saldo glosado.`);
    } else {
      parts.push("Nas contas recebidas do período, não há saldo financeiro aberto nem saldo glosado.");
    }
    return parts.join(" ");
  })();

  return (
    <div className="app-shell">
      <header className="topbar v6-topbar">
        <div className="institution-brand">
          <div className="dashboard-logo-stage"><img src={`${import.meta.env.BASE_URL}hospital-demo-logo.svg`} alt="Hospital Demonstrativo" /></div>
          <div className="brand-copy">
            <div className="eyebrow">HOSPITAL DEMONSTRATIVO · ONCOLOGIA</div>
            <h1>Gestão Integrada da Oncologia</h1>
            <p>Clareza nas informações, rastreabilidade no processo e leitura executiva para melhores decisões.</p>
          </div>
        </div>
        <div className="user-toolbar">
          <label>Convênio<select value={convenio?.cd_convenio || ""} onChange={(e)=>onConvenioChange?.(e.target.value)}>{convenios.map(c=><option key={c.cd_convenio} value={c.cd_convenio}>{c.nm_convenio} · {c.cd_convenio}{c.modelo_homologado?"":" · não homologado"}</option>)}</select></label>
          <div className="user-chip"><strong>{session?.user?.display_name}</strong><span>{String(session?.user?.role || "").replaceAll("_"," ")}</span></div>
          <button className="logout-button" type="button" onClick={onLogout}>Sair</button>
          <div className="topbar-status"><span className="dot" /> Oracle read-only</div>
        </div>
      </header>

      <div className="workspace-layout">
        <aside className="side-nav" aria-label="Navegação principal">
          <div className="side-nav-title">Navegação</div>
          <div className="side-nav-group"><span>Visão geral</span><button type="button" className={tab === "resumo" ? "active" : ""} onClick={()=>setTab("resumo")}>Resumo integrado</button></div>
          {role !== "VISUALIZACAO" && <div className="side-nav-group"><span>Assistencial</span><button type="button" className={tab === "contas" && contasView === "pacientes" ? "active" : ""} onClick={()=>{setTab("contas");setContasView("pacientes");setSearch("");}}>Pacientes</button><button type="button" className={tab === "contas" && contasView === "atendimentos" ? "active" : ""} onClick={()=>{setTab("contas");setContasView("atendimentos");setSearch("");}}>Contas</button></div>}
          {role !== "VISUALIZACAO" && <div className="side-nav-group"><span>Financeiro</span><button type="button" className={tab === "recebimentos" ? "active" : ""} onClick={()=>setTab("recebimentos")}>Recebimentos</button><button type="button" className={tab === "pendencias" && pendenciasView === "glosas" ? "active" : ""} onClick={()=>{setTab("pendencias");setPendenciasView("glosas");}}>Glosas</button><button type="button" className={tab === "pendencias" && pendenciasView === "auditoria" ? "active" : ""} onClick={()=>{setTab("pendencias");setPendenciasView("auditoria");}}>Pendências</button></div>}
          <div className="side-nav-group"><span>Análises</span><button type="button" className={tab === "analises" ? "active" : ""} onClick={()=>setTab("analises")}>Indicadores</button>{role !== "VISUALIZACAO" && <button type="button" className={tab === "relatorios" ? "active" : ""} onClick={()=>setTab("relatorios")}>Relatórios</button>}</div>
          {role === "ADMIN" && <div className="side-nav-group"><span>Governança</span><button type="button" className={tab === "admin" ? "active" : ""} onClick={()=>setTab("admin")}>Administração</button></div>}
        </aside>
        <main className="workspace-main">
        <form className="filters" onSubmit={aplicar}>
          <label>Data inicial<input type="date" value={inicio} onChange={(e) => setInicio(e.target.value)} /></label>
          <label>Data final<input type="date" value={fim} onChange={(e) => setFim(e.target.value)} /></label>
          <button type="submit">Atualizar período</button>
          <button type="button" className="privacy-button" onClick={() => setPrivacy((v) => !v)}>{privacy ? "Mostrar nomes" : "Ocultar nomes"}</button>
          <div className="period-chip">{shortDate(fInicio)} - {shortDate(fFim)}</div>
        </form>


        {!convenioSupported && (
          <div className="convenio-gate">
            <span className="gate-kicker">ESTRUTURA MULTI-CONVÊNIO ATIVA</span>
            <h2>{convenio?.nm_convenio || "Convênio selecionado"}</h2>
            <p>Seu usuário possui acesso a este convênio, mas as regras de oncologia, faturamento e recebimento ainda precisam ser homologadas antes de exibir indicadores. Isso evita reutilizar regras do CONVENIO_DEMO em outro contrato.</p>
            <strong>Modelo validado atualmente: CONVENIO_DEMO · código 11.</strong>
          </div>
        )}

        {convenioSupported && erro && <div className="error">{erro}</div>}
        {convenioSupported && (loadingBase ? <div className="loading-panel">Carregando indicadores principais…</div> : (
          <>
            {tab === "contas" && (
              <SubTabs
                value={contasView}
                onChange={(v) => { setContasView(v); setSearch(""); }}
                items={[["atendimentos", "Contas e atendimentos"], ["pacientes", "Pacientes"]]}
              />
            )}
            {tab === "pendencias" && (
              <SubTabs
                value={pendenciasView}
                onChange={(v) => { setPendenciasView(v); setSearch(""); }}
                items={[["auditoria", "Pendências e auditoria"], ["glosas", "Glosas"]]}
              />
            )}
            {tab === "analises" && (
              <SubTabs
                value={analisesView}
                onChange={(v) => { setAnalisesView(v); setSearch(""); }}
                items={role === "VISUALIZACAO" ? [["faturamentoMv", "Faturamento MV"], ["producao", "Produção"]] : [["faturamentoMv", "Faturamento MV"], ["producao", "Produção"], ["produtos", "Produtos"]]}
              />
            )}

            {tab === "resumo" && (
              <>
                <div className="summary-hero">
                  <div>
                    <span className="summary-kicker">LEITURA EXECUTIVA</span>
                    <h2>Da produção ao que ainda exige ação</h2>
                    <p>Uma leitura única para gestão, sem misturar as datas de produção, competência e recebimento.</p>
                  </div>
                  <div className="summary-validation">
                    <strong>Faturamento MV conciliado</strong>
                    <span>Regra conferida com o relatório nativo · setor 113</span>
                  </div>
                </div>

                {loading.integrated ? <div className="loading-panel">Integrando produção, faturamento, recebimentos e pendências…</div> : !loaded.integrated ? (
                  <div className="empty-state" role="status">
                    <strong>Resumo integrado indisponível.</strong><br />
                    Os valores não serão apresentados como zero enquanto a consulta não for concluída com sucesso.
                    <div style={{ marginTop: "12px" }}>
                      <button className="secondary-button" type="button" onClick={loadIntegrated}>Tentar novamente</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="executive-reading" aria-live="polite">
                      <span>O que aconteceu neste período</span>
                      <p>{executiveSentence}</p>
                    </div>

                    <div className="journey-track" aria-label="Jornada financeira da oncologia">
                      <JourneyStep
                        step="1"
                        title="Produção"
                        value={brl(producaoValor)}
                        detail={`${int(integrado.producao?.qt_atendimentos)} atendimentos · ${int(integrado.producao?.qt_contas)} contas`}
                        dateLabel="Por data de produção"
                        tone="production"
                        onClick={() => { setTab("analises"); setAnalisesView("producao"); }}
                      />
                      <JourneyStep
                        step="2"
                        title="Faturamento MV"
                        value={brl(faturadoMvValor)}
                        state={faturadoMvValor > 0 ? null : "Nenhum faturamento fechado"}
                        detail={faturadoMvValor > 0 ? `${int(integrado.faturamento_mv?.qt_contas)} contas · faturamento oficial` : "Nenhum valor identificado na competência selecionada"}
                        dateLabel="Por competência MV"
                        tone={faturadoMvValor > 0 ? "billing" : "empty"}
                        onClick={() => { setTab("analises"); setAnalisesView("faturamentoMv"); }}
                      />
                      <JourneyStep
                        step="3"
                        title="Recebimentos"
                        value={brl(recebidoBaseValor)}
                        state={recebidoBaseValor > 0 ? null : "Nenhum recebimento registrado"}
                        detail={recebidoBaseValor > 0 ? `${int(integrado.recebimentos?.qt_contas)} contas · ${int(integrado.recebimentos?.qt_eventos)} evento(s)` : "O financeiro não registrou recebimentos neste intervalo"}
                        dateLabel="Por data financeira"
                        tone={recebidoBaseValor > 0 ? "receipt" : "empty"}
                        onClick={() => setTab("recebimentos")}
                      />
                      <JourneyStep
                        step="4"
                        title="Glosas"
                        value={brl(glosaRecebimentoValor)}
                        state={glosaRecebimentoValor > 0 ? null : "Nenhuma glosa identificada"}
                        detail={glosaRecebimentoValor > 0 ? "Valor glosado nos eventos financeiros do período" : "Sem glosa nos recebimentos identificados"}
                        dateLabel="Associada aos recebimentos"
                        tone={glosaRecebimentoValor > 0 ? "warning" : "empty"}
                        onClick={() => { setTab("pendencias"); setPendenciasView("glosas"); }}
                      />
                      <JourneyStep
                        step="5"
                        title="Pendências"
                        value={brl(totalPendenciasRecebidas)}
                        state={totalPendenciasRecebidas > 0 ? null : "Sem pendências financeiras"}
                        detail={`Aberto ${brl(saldoFinanceiroValor)} · glosado ${brl(saldoGlosadoValor)}`}
                        dateLabel="Nas contas recebidas do período"
                        tone={totalPendenciasRecebidas > 0 ? "warning" : "ok"}
                        onClick={() => { setTab("pendencias"); setPendenciasView("auditoria"); }}
                      />
                    </div>

                    <details className="method-details">
                      <summary>Como estes números são calculados?</summary>
                      <p className="method-intro">Cada etapa respeita a data correta do MV. Por isso, produção, faturamento e recebimento do mesmo intervalo não devem ser subtraídos diretamente.</p>
                      <div className="scope-grid compact">
                        <ScopeCard title="Produção" field="ITREG_AMB.DT_PRODUCAO">O que a oncologia realizou no período.</ScopeCard>
                        <ScopeCard title="Faturamento MV" field="FATURA.DT_COMPETENCIA">O que entrou no faturamento oficial por competência.</ScopeCard>
                        <ScopeCard title="Recebimentos" field="RECCON_REC.DT_RECEBIMENTO">O que o financeiro registrou como recebido; pode vir de competências anteriores.</ScopeCard>
                      </div>
                      <div className="precision-banner"><strong>Importante:</strong> use a origem dos recebimentos para saber de quais competências veio o dinheiro. O painel mantém as métricas integradas na leitura, mas não mistura suas bases temporais.</div>
                    </details>

                    <Section title="Qualidade da informação" subtitle="Sinais que merecem conferência antes de uma conclusão financeira.">
                      <div className="quality-grid">
                        <div><span>Sem nota fiscal</span><strong>{int(integrado.qualidade_producao?.qt_sem_nota)}</strong></div>
                        <div><span>Sem recebimento identificado</span><strong>{int(integrado.qualidade_producao?.qt_sem_recebimento)}</strong></div>
                        <div><span>Remessa paga sem recebimento</span><strong>{int(integrado.qualidade_producao?.qt_remessa_paga_sem_recebimento)}</strong></div>
                        <div><span>Recebido maior que faturado</span><strong>{int(integrado.qualidade_producao?.qt_receb_maior_faturado)}</strong></div>
                      </div>
                      {integrado.alertas?.length ? (
                        <div className="alerts-list">
                          {integrado.alertas.map((a, idx) => (
                            <div key={`${a.tipo}-${idx}`} className={`alert-item ${a.nivel === "critico" ? "critical" : "attention"}`}>
                              <strong>{a.texto}</strong>
                              <span>{a.quantidade != null ? `${int(a.quantidade)} ocorrência(s)` : brl(a.valor)}</span>
                            </div>
                          ))}
                        </div>
                      ) : <div className="quality-ok">Nenhum alerta de qualidade nas regras automáticas desta leitura.</div>}
                    </Section>

                    <Section title="Navegação orientada" subtitle="Entre no detalhe só quando precisar investigar.">
                      <div className="guided-actions">
                        <button type="button" onClick={() => { setTab("contas"); setContasView("atendimentos"); }}><strong>Contas e pacientes</strong><span>Quem gerou os valores e qual é a situação de cada conta.</span></button>
                        <button type="button" onClick={() => setTab("recebimentos")}><strong>Recebimentos</strong><span>Eventos financeiros, competência de origem, aging e composição.</span></button>
                        <button type="button" onClick={() => { setTab("pendencias"); setPendenciasView("auditoria"); }}><strong>Glosas e pendências</strong><span>O que exige conferência ou ação da equipe.</span></button>
                        <button type="button" onClick={() => { setTab("analises"); setAnalisesView("faturamentoMv"); }}><strong>Análises</strong><span>Faturamento MV, produção e produtos com metodologia explícita.</span></button>
                      </div>
                    </Section>
                  </>
                )}
              </>
            )}

            {tab === "analises" && analisesView === "producao" && (
              <>
                <ScopeNote><strong>Período desta visão:</strong> coorte de produção oncológica CONVENIO_DEMO por <strong>ITREG_AMB.DT_PRODUCAO</strong>. Não confundir com faturamento por competência; para conciliar com o relatório nativo, use <strong>Análises → Faturamento MV</strong>.</ScopeNote>
                <div className="funnel-strip">
                  <div><span>Valor das contas</span><strong>{brl(financeiro.vl_faturado)}</strong><small>coorte de produção</small></div>
                  <i>→</i>
                  <div><span>Remetido</span><strong>{brl(financeiro.vl_remetido)}</strong><small>coorte de produção</small></div>
                  <i>→</i>
                  <div className="funnel-action" onClick={() => setTab("recebimentos")}><span>Recebimentos</span><strong>abrir</strong><small>data financeira</small></div>
                  <i>→</i>
                  <div><span>Glosa líquida</span><strong>{brl(financeiro.vl_glosa_liquida)}</strong><small>coorte de produção</small></div>
                </div>

                <div className="metrics-grid">
                  <Card title="Valor das contas (produção)" value={brl(financeiro.vl_faturado)} subtitle={`${int(financeiro.qt_contas)} contas`} />
                  <Card title="Remetido (produção)" value={brl(financeiro.vl_remetido)} subtitle={pct(financeiro.pct_remetido_faturado)} />
                  <Card title="Não remetido" value={brl(financeiro.vl_nao_remetido)} />
                  <Card title="Em remessas marcadas pagas" value={brl(financeiro.vl_remessas_pagas)} subtitle="status operacional" tone="good" />
                  <Card title="Glosa bruta" value={brl(financeiro.vl_glosa_bruta)} subtitle={`${int(financeiro.qt_contas_com_glosa)} contas`} tone="danger" />
                  <Card title="Glosa líquida" value={brl(financeiro.vl_glosa_liquida)} subtitle={pct(financeiro.pct_glosa_liquida_remetido, 4)} tone="danger" />
                </div>

                <div className="precision-banner">
                  <strong>Precisão:</strong> esta visão mede a coorte de produção. O faturamento contábil por competência está em <strong>Análises → Faturamento MV</strong>; os recebimentos reais ficam em <strong>Recebimentos</strong>.
                </div>

                <Section title="Indicadores do período" subtitle={financeiro.semantica_periodo}>
                  <div className="mini-metrics">
                    <Card title="Atendimentos" value={int(financeiro.qt_atendimentos || resumo.atendimentos_com_faturamento)} />
                    <Card title="Contas" value={int(financeiro.qt_contas)} />
                    <Card title="Remessas" value={int(financeiro.qt_remessas)} />
                    <Card title="Produtos" value={int(resumo.produtos_distintos)} />
                  </div>
                </Section>

                <Section title="Evolução da coorte de produção" subtitle="Agrupamento pela data de lançamento da conta da coorte selecionada. Não equivale a FATURA.DT_COMPETENCIA e não representa mês de recebimento.">
                  {loading.mensal ? <div className="empty-state">Carregando gráfico…</div> : mensal.length ? (
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={mensal}>
                          <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="mes" /><YAxis width={88} />
                          <Tooltip formatter={(v) => brl(v)} /><Legend />
                          <Line type="monotone" dataKey="vl_faturado" name="Valor das contas" strokeWidth={2} />
                          <Line type="monotone" dataKey="vl_remetido" name="Remetido" strokeWidth={2} />
                          <Line type="monotone" dataKey="vl_remessas_pagas" name="Em remessas pagas" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : <div className="empty-state">Sem dados para o período.</div>}
                </Section>

                <Section
                  title="Comparação com o período anterior"
                  subtitle="Mesma quantidade de dias imediatamente anterior. Faturamento e recebimento mantêm suas próprias bases temporais."
                  actions={<button className="secondary-button" type="button" onClick={() => runLazy("comparativo", () => api.comparativo(fInicio, fFim), setComparativo)}>Carregar comparação</button>}
                >
                  {loading.comparativo ? <div className="empty-state">Calculando comparação…</div> : comparativo?.metricas ? (
                    <DataTable
                      keyField="indicador"
                      rows={comparativo.metricas}
                      columns={[
                        { key: "indicador", label: "Indicador" },
                        { key: "anterior", label: "Anterior", render: (v, r) => r.indicador.includes("Contas") ? int(v) : brl(v), className: "number" },
                        { key: "atual", label: "Atual", render: (v, r) => r.indicador.includes("Contas") ? int(v) : brl(v), className: "number" },
                        { key: "variacao_pct", label: "Variação", render: (v) => v == null ? "n/a" : `${Number(v) >= 0 ? "+" : ""}${pct(v)}`, className: "number" },
                      ]}
                    />
                  ) : <div className="empty-state">Carregue somente quando precisar comparar os períodos.</div>}
                </Section>
              </>
            )}

            {tab === "analises" && analisesView === "faturamentoMv" && (
              <>
                <ScopeNote><strong>Período desta aba:</strong> <strong>FATURA.DT_COMPETENCIA</strong>. Esta é a visão indicada para conciliar o painel com o relatório nativo enviado. Para competência mensal, selecione um intervalo que inclua a data de competência gravada na fatura (normalmente o início do mês).</ScopeNote>

                <Section
                  title="Faturamento por competência MV"
                  subtitle="Regra estrutural do relatório nativo: empresa 1, CONVENIO_DEMO 11, remessa fechada, conta/item fechado, não pacote, não diagnóstico e pagamento não cancelado; soma item a item."
                  actions={
                    <div className="action-row">
                      <input
                        className="search"
                        placeholder="Setores do relatório: ex. 113"
                        value={setoresMv}
                        onChange={(e) => setSetoresMv(e.target.value)}
                        aria-label="Códigos de setor do relatório MV"
                      />
                      <button className="secondary-button" type="button" onClick={loadFaturamentoMv}>Aplicar setores</button>
                    </div>
                  }
                >
                  <div className="precision-banner pending">
                    <strong>Conciliação 1:1:</strong> informe os mesmos códigos de setor usados no relatório nativo. O painel não adiciona filtro por AGENDAMENTO_ONCOLOGICO nesta aba, porque ele não existe na SQL nativa enviada. O setor 113 (ONCOLOGIA) vem preenchido por padrão. O placeholder <code>V_VAR</code> ainda não foi reproduzido porque sua regra não foi fornecida; nenhum SQL livre é aceito pelo painel.
                  </div>

                  {loading.faturamentoMv ? <div className="loading-panel">Calculando faturamento por competência MV…</div> : (
                    <>
                      <div className="metrics-grid">
                        <Card title="Faturamento competência MV" value={brl(fatMvResumo.vl_faturamento_competencia)} subtitle={`${int(fatMvResumo.qt_itens)} itens`} />
                        <Card title="Ambulatorial" value={brl(fatMvResumo.vl_ambulatorial)} subtitle={`${int(fatMvResumo.qt_itens_ambulatorial)} itens`} />
                        <Card title="Hospitalar" value={brl(fatMvResumo.vl_hospitalar)} subtitle={`${int(fatMvResumo.qt_itens_hospitalar)} itens`} />
                        <Card title="Contas" value={int(fatMvResumo.qt_contas)} subtitle={`${int(fatMvResumo.qt_atendimentos)} atendimentos`} />
                        <Card title="Remessas" value={int(fatMvResumo.qt_remessas)} />
                        <Card title="Setores" value={int(fatMvResumo.qt_setores)} subtitle={fatMvResumo.setores_aplicados?.length ? `Filtro: ${fatMvResumo.setores_aplicados.join(", ")}` : "Todos os setores CONVENIO_DEMO"} />
                      </div>

                      <div className="inline-note">
                        <strong>Diferença para Produção:</strong> aqui o valor é somado item a item e o período usa a competência da fatura. A análise de Produção usa contas da coorte por DT_PRODUCAO.
                      </div>
                    </>
                  )}
                </Section>

                <Section title="Evolução por competência MV" subtitle="Agrupamento mensal por FATURA.DT_COMPETENCIA.">
                  {loading.faturamentoMv ? <div className="empty-state">Consultando competências…</div> : fatMvMensal.length ? (
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={fatMvMensal}>
                          <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="competencia" /><YAxis width={88} />
                          <Tooltip formatter={(v) => brl(v)} /><Legend />
                          <Line type="monotone" dataKey="vl_faturamento_competencia" name="Total MV" strokeWidth={2} />
                          <Line type="monotone" dataKey="vl_ambulatorial" name="Ambulatorial" strokeWidth={2} />
                          <Line type="monotone" dataKey="vl_hospitalar" name="Hospitalar" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : <div className="empty-state">Sem faturamento por competência para os filtros informados.</div>}
                </Section>

                <Section
                  title="Composição por setor"
                  subtitle="Use esta tabela para conferir exatamente quais setores formam o total e alinhar com a seleção do relatório nativo."
                  actions={<a className="secondary-link" href={api.faturamentoMvCsvUrl(fInicio, fFim, setoresMv.trim())}>Exportar CSV</a>}
                >
                  {loading.faturamentoMv ? <div className="empty-state">Consultando setores…</div> : (
                    <DataTable
                      keyField="cd_setor"
                      rows={fatMvSetores}
                      columns={[
                        { key: "cd_setor", label: "Cód. setor" },
                        { key: "nm_setor", label: "Setor" },
                        { key: "vl_faturamento_competencia", label: "Faturamento MV", render: brl, className: "number" },
                        { key: "vl_ambulatorial", label: "Ambulatorial", render: brl, className: "number" },
                        { key: "vl_hospitalar", label: "Hospitalar", render: brl, className: "number" },
                        { key: "qt_itens", label: "Itens", render: int, className: "number" },
                        { key: "qt_contas", label: "Contas", render: int, className: "number" },
                        { key: "qt_remessas", label: "Remessas", render: int, className: "number" },
                      ]}
                    />
                  )}
                </Section>
              </>
            )}

            {tab === "recebimentos" && (
              <>
                <ScopeNote><strong>Período desta aba:</strong> <strong>Data de recebimento registrada no financeiro</strong> (`RECCON_REC.DT_RECEBIMENTO`). Não é inferida como data bancária.</ScopeNote>
                {loading.paymentsCore ? <div className="loading-panel">Conciliando recebimentos do período…</div> : (
                  <>
                    <div className="metrics-grid payments-grid">
                      <Card title="Recebimento financeiro" value={brl(pagResumo.vl_recebido_financeiro)} subtitle={`${int(pagResumo.qt_eventos_recebimento)} eventos`} tone="good" />
                      <Card title="Recebimento base" value={brl(pagResumo.vl_recebido_base)} subtitle="financeiro - acréscimos" />
                      <Card title="Acréscimos" value={brl(pagResumo.vl_acrescimo)} />
                      <Card title="Contas recebidas" value={int(pagResumo.qt_contas_recebidas)} subtitle={`${int(pagResumo.qt_remessas_recebidas)} remessas`} />
                      <Card title="Pacientes" value={int(pagResumo.qt_pacientes)} subtitle={`${int(pagResumo.qt_atendimentos)} atendimentos`} />
                      <Card title="Itens com múltiplos recebimentos" value={int(pagResumo.qt_itens_multiplos_recebimentos)} subtitle={`máx. ${int(pagResumo.max_recebimentos_por_item)} por item`} tone="pending" />
                    </div>

                    <Section title="Prazo de recebimento" subtitle="Dias entre o atendimento e cada evento financeiro vinculado à conta.">
                      <div className="mini-metrics aging-grid">
                        <Card title="Prazo médio" value={`${num(pagAging.dias_medio)} dias`} />
                        <Card title="P50 (mediana)" value={`${num(pagAging.dias_p50)} dias`} />
                        <Card title="P90" value={`${num(pagAging.dias_p90)} dias`} />
                        <Card title="Acima de 90 dias" value={pct(pagAging.pct_acima_90)} subtitle={`${int(pagAging.qt_acima_90)} conta-evento`} tone="pending" />
                      </div>
                      <div className="aging-buckets">
                        <span>≤30 dias <strong>{int(pagAging.qt_ate_30)}</strong></span>
                        <span>31–60 <strong>{int(pagAging.qt_31_60)}</strong></span>
                        <span>61–90 <strong>{int(pagAging.qt_61_90)}</strong></span>
                        <span>&gt;90 <strong>{int(pagAging.qt_acima_90)}</strong></span>
                      </div>
                    </Section>

                    <Section
                      title="Quando cada competência foi paga"
                      subtitle="Acompanhe de qual competência veio o valor e em quais meses os recebimentos foram registrados."
                    >
                      {competenciaTimeline.length ? (
                        <div className="competency-timeline">
                          {competenciaTimeline.map((item) => {
                            const total = item.recebido + item.glosa;
                            const pctRecebido = total > 0 ? (item.recebido / total) * 100 : 0;
                            const pctGlosa = total > 0 ? (item.glosa / total) * 100 : 0;

                            return (
                              <div className="competency-card" key={item.competencia}>
                                <div className="competency-card-head">
                                  <div>
                                    <span className="competency-label">Competência</span>
                                    <strong>{item.competencia}</strong>
                                  </div>

                                  <div className="competency-summary">
                                    <span>
                                      Recebido <strong>{brl(item.recebido)}</strong>
                                    </span>
                                    <span>
                                      Glosa <strong>{brl(item.glosa)}</strong>
                                    </span>
                                  </div>
                                </div>

                                <div className="competency-bar">
                                  <span
                                    className="competency-bar-received"
                                    style={{ width: `${pctRecebido}%` }}
                                    title={`Recebido ${brl(item.recebido)}`}
                                  />
                                  <span
                                    className="competency-bar-denied"
                                    style={{ width: `${pctGlosa}%` }}
                                    title={`Glosa ${brl(item.glosa)}`}
                                  />
                                </div>

                                <div className="competency-flow">
                                  <div className="competency-origin">
                                    <strong>{item.competencia}</strong>
                                    <small>competência de origem</small>
                                  </div>

                                  <div className="competency-arrow">→</div>

                                  <div className="competency-events">
                                    {item.meses.map((evento) => (
                                      <div className="competency-event" key={`${item.competencia}-${evento.mes}`}>
                                        <strong>{evento.mes}</strong>
                                        <span className="event-received">
                                          + {brl(evento.recebido)} recebido
                                        </span>
                                        {evento.glosa > 0 && (
                                          <span className="event-denied">
                                            {brl(evento.glosa)} glosa
                                          </span>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="empty-state">
                          Sem recebimentos vinculados a competências neste período.
                        </div>
                      )}

                      <div className="inline-note">
                        Leia da esquerda para a direita: a competência indica a origem do faturamento;
                        os cartões seguintes mostram em quais meses houve recebimento e qual glosa
                        foi registrada nesses eventos financeiros.
                      </div>
                    </Section>

                    <Section title="Origem dos recebimentos" subtitle="De quais competências vieram os valores recebidos dentro do período selecionado.">
                      {origemRecebimentos.length ? (
                        <div className="chart-wrap compact-chart">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={origemRecebimentos} layout="vertical" margin={{ left: 18, right: 24 }}>
                              <CartesianGrid strokeDasharray="3 3" /><XAxis type="number" tickFormatter={(v) => Number(v).toLocaleString("pt-BR", { notation: "compact" })} />
                              <YAxis dataKey="competencia" type="category" width={85} />
                              <Tooltip formatter={(v) => brl(v)} /><Bar dataKey="valor" name="Recebimento financeiro" />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      ) : <div className="empty-state">Sem recebimentos no período.</div>}
                    </Section>

                    <Section title="Matriz competência × recebimento" subtitle="Linhas são competências de origem; colunas são meses em que o recebimento foi registrado no financeiro. Quanto mais intenso o fundo, maior o valor.">
                      <ReceiptMatrix rows={receiptMatrix} />
                    </Section>

                    <Section
                      title="Eventos de recebimento"
                      subtitle="Cada linha é um CD_RECCON_REC. Clique em um evento para abrir os itens, contas, pacientes e remessas que o compõem."
                      actions={<button className="secondary-button" type="button" onClick={() => runLazy("pagEventos", () => api.pagamentosEventos(fInicio, fFim, 500), setPagEventos)}>Carregar eventos</button>}
                    >
                      {loading.pagEventos ? <div className="empty-state">Consultando eventos…</div> : pagEventos.length ? (
                        <DataTable columns={eventCols} rows={pagEventos} keyField="cd_reccon_rec" onRowClick={abrirEvento} />
                      ) : <div className="empty-state">Carregue os eventos somente quando precisar do drill-down.</div>}
                    </Section>

                    {selectedEvent && (
                      <Section
                        title={`Evento ${selectedEvent.cd_reccon_rec}`}
                        subtitle={`${shortDate(selectedEvent.dt_recebimento)} · parcela oncológica ${brl(selectedEvent.vl_onco_recebido)} de um evento total de ${brl(selectedEvent.vl_evento_total)}`}
                        actions={<button className="secondary-button" type="button" onClick={() => { setSelectedEvent(null); setEventItems([]); }}>Fechar detalhe</button>}
                      >
                        {loading.eventItems ? <div className="empty-state">Abrindo composição do evento…</div> : (
                          <DataTable columns={eventItemCols} rows={eventItems} keyField="cd_itfat_nf" />
                        )}
                      </Section>
                    )}

                    <Section
                      title="Contas recebidas no período"
                      subtitle="Mostra o valor recebido no período e o saldo estimado considerando os recebimentos acumulados da conta."
                      actions={<div className="action-row"><input className="search" placeholder="Paciente, atendimento, conta ou remessa" value={search} onChange={(e) => setSearch(e.target.value)} /><button className="secondary-button" type="button" onClick={() => runLazy("pagContas", () => api.pagamentosContas(fInicio, fFim, 500), setPagContas)}>Carregar contas</button></div>}
                    >
                      {loading.pagContas ? <div className="empty-state">Consultando contas…</div> : pagContas.length ? (
                        <DataTable columns={paymentAccountCols} rows={filterRows(pagContas, ["nm_paciente", "cd_atendimento", "cd_reg_amb", "cd_remessa", "status_recebimento"])} keyField="cd_reg_amb" onRowClick={abrirConta} />
                      ) : <div className="empty-state">Carregue as contas para investigar a composição individual.</div>}
                    </Section>
                  </>
                )}
              </>
            )}

            {tab === "contas" && contasView === "atendimentos" && (
              <>
                <ScopeNote><strong>Período:</strong> produção oncológica. Os recebimentos exibidos são acumulados da conta e podem ocorrer depois do período de produção.</ScopeNote>
                <Section
                  title="Atendimentos e contas"
                  subtitle="Paciente → atendimento → conta → remessa → recebimento → glosa → saldo."
                  actions={<input className="search" placeholder="Buscar paciente, atendimento, conta ou remessa" value={search} onChange={(e) => setSearch(e.target.value)} />}
                >
                  {capabilities.custo_medicamento && <div className="inline-note">* Custo medicamento vem de FA_CUSTO_ATENDIMENTO e não representa o custo hospitalar total.</div>}
                  {loading.atendimentos ? <div className="empty-state">Consultando atendimentos…</div> : (
                    <DataTable columns={atendCols} rows={filterRows(atendimentos, ["nm_paciente", "cd_paciente", "cd_atendimento", "cd_reg_amb", "cd_remessa", "status_financeiro"])} keyField="cd_reg_amb" onRowClick={abrirConta} />
                  )}
                </Section>
              </>
            )}

            {tab === "contas" && contasView === "pacientes" && (
              <>
                <ScopeNote><strong>Período:</strong> produção oncológica. O consolidado inclui recebimentos acumulados vinculados às contas desse coorte.</ScopeNote>
                <Section
                  title="Consolidado por paciente"
                  subtitle="Faturado, recebido, saldo, glosa e valores médios por atendimento."
                  actions={<input className="search" placeholder="Buscar paciente" value={search} onChange={(e) => setSearch(e.target.value)} />}
                >
                  {capabilities.custo_medicamento && <div className="inline-note">* Custo medicamento é uma dimensão parcial de custo. Não representa custo hospitalar total.</div>}
                  {loading.pacientes ? <div className="empty-state">Consultando pacientes…</div> : (
                    <DataTable columns={pacCols} rows={filterRows(pacientes, ["nm_paciente", "cd_paciente"])} keyField="cd_paciente" onRowClick={abrirPaciente} />
                  )}
                </Section>
              </>
            )}

            {tab === "pendencias" && pendenciasView === "auditoria" && (
              <>
                <ScopeNote><strong>Auditoria da Produção:</strong> o período seleciona contas produzidas no intervalo e verifica o histórico financeiro acumulado delas. Não confundir com os recebimentos ocorridos no mesmo intervalo.</ScopeNote>
                <div className="metrics-grid audit-grid">
                  <Card title="Sem nota fiscal" value={int(audResumo.qt_sem_nota)} tone={Number(audResumo.qt_sem_nota) ? "pending" : "good"} />
                  <Card title="Sem recebimento" value={int(audResumo.qt_sem_recebimento)} tone={Number(audResumo.qt_sem_recebimento) ? "pending" : "good"} />
                  <Card title="Remessa paga sem recebimento" value={int(audResumo.qt_remessa_paga_sem_recebimento)} tone={Number(audResumo.qt_remessa_paga_sem_recebimento) ? "danger" : "good"} />
                  <Card title="Recebido > faturado" value={int(audResumo.qt_receb_maior_faturado)} tone={Number(audResumo.qt_receb_maior_faturado) ? "danger" : "good"} />
                  <Card title="Parcialmente recebidas" value={int(audResumo.qt_parcialmente_recebida)} tone="pending" />
                  <Card title="Recebidas com glosa" value={int(audResumo.qt_recebida_com_glosa)} tone="pending" />
                  <Card title="Saldo financeiro aberto" value={brl(audResumo.vl_saldo_financeiro_aberto)} />
                  <Card title="Saldo glosado" value={brl(audResumo.vl_saldo_glosado)} tone="danger" />
                </div>
                <Section
                  title="Exceções e pendências"
                  subtitle="Regras automáticas para localizar contas que merecem conferência. Múltiplos recebimentos não são necessariamente erro."
                  actions={<button className="secondary-button" type="button" onClick={() => runLazy("audDetalhe", () => api.auditoriaDetalhe(fInicio, fFim, 500), setAudDetalhe)}>Carregar detalhes</button>}
                >
                  {loading.audDetalhe ? <div className="empty-state">Executando auditoria…</div> : audDetalhe.length ? (
                    <DataTable
                      keyField="cd_reg_amb"
                      rows={audDetalhe}
                      columns={[
                        { key: "tipo", label: "Regra", render: (v) => <StatusBadge value={v} /> },
                        { key: "nm_paciente", label: "Paciente", render: patientName },
                        { key: "cd_atendimento", label: "Atendimento" },
                        { key: "cd_reg_amb", label: "Conta" },
                        { key: "cd_remessa", label: "Remessa" },
                        { key: "sn_paga", label: "SN_PAGA" },
                        { key: "qt_eventos_recebimento", label: "Eventos", render: int, className: "number" },
                        { key: "vl_faturado", label: "Faturado", render: brl, className: "number" },
                        { key: "vl_recebido_base", label: "Recebido base", render: brl, className: "number" },
                        { key: "vl_glosa_recebimento", label: "Glosa", render: brl, className: "number" },
                        { key: "vl_saldo_financeiro_aberto", label: "Saldo aberto", render: brl, className: "number" },
                        { key: "vl_saldo_glosado", label: "Saldo glosado", render: brl, className: "number" },
                      ]}
                    />
                  ) : <div className="empty-state">Carregue o detalhamento apenas quando for revisar as exceções.</div>}
                </Section>

                <Section
                  title="Auditoria dos recebimentos"
                  subtitle="Aqui o período é financeiro: RECCON_REC.DT_RECEBIMENTO. Audita apenas as contas que tiveram recebimento no intervalo."
                  actions={<div className="action-row"><button className="secondary-button" type="button" onClick={() => runLazy("audRecResumo", () => api.auditoriaRecebimentosResumo(fInicio, fFim), setAudRecResumo)}>Carregar resumo</button><button className="secondary-button" type="button" onClick={() => runLazy("audRecDetalhe", () => api.auditoriaRecebimentosDetalhe(fInicio, fFim, 500), setAudRecDetalhe)}>Carregar pendências</button></div>}
                >
                  {loading.audRecResumo ? <div className="empty-state">Auditando recebimentos…</div> : audRecResumo.qt_contas != null ? (
                    <div className="mini-metrics">
                      <Card title="Contas recebidas" value={int(audRecResumo.qt_contas)} />
                      <Card title="Recebidas" value={int(audRecResumo.qt_recebidas)} tone="good" />
                      <Card title="Recebidas com glosa" value={int(audRecResumo.qt_recebidas_com_glosa)} tone="pending" />
                      <Card title="Parciais" value={int(audRecResumo.qt_parcialmente_recebidas)} tone="pending" />
                      <Card title="Saldo aberto" value={brl(audRecResumo.vl_saldo_financeiro_aberto)} />
                      <Card title="Saldo glosado" value={brl(audRecResumo.vl_saldo_glosado)} tone="danger" />
                    </div>
                  ) : <div className="empty-state">Carregue o resumo para auditar o período de recebimento.</div>}
                  {loading.audRecDetalhe ? <div className="empty-state">Carregando pendências dos recebimentos…</div> : audRecDetalhe.length ? (
                    <DataTable
                      keyField="cd_reg_amb"
                      rows={audRecDetalhe}
                      columns={paymentAccountCols}
                    />
                  ) : null}
                </Section>
              </>
            )}

            {tab === "pendencias" && pendenciasView === "glosas" && (
              <>
                <ScopeNote><strong>Período:</strong> contas do coorte de produção selecionado. A data do evento de glosa é exibida no detalhamento.</ScopeNote>
                <Section
                  title="Competências acompanhadas até a situação atual"
                  subtitle="O período seleciona a produção. Depois acompanhamos faturamento, pagamentos posteriores, glosa e saldo atual dessas contas."
                >
                  {loading.historicoCompetencias ? (
                    <div className="loading-panel">Montando histórico financeiro das competências…</div>
                  ) : historicoCompetencias.length ? (
                    <div className="competency-timeline">
                      {Array.from(
                        historicoCompetencias.reduce((map, row) => {
                          const key = row.competencia || "Sem competência";

                          if (!map.has(key)) {
                            map.set(key, {
                              competencia: key,
                              qt_contas: Number(row.qt_contas || 0),
                              vl_faturado: Number(row.vl_faturado || 0),
                              vl_recebido_financeiro: Number(row.vl_recebido_financeiro || 0),
                              vl_recebido_base: Number(row.vl_recebido_base || 0),
                              vl_glosa: Number(row.vl_glosa || 0),
                              vl_em_aberto: Number(row.vl_em_aberto || 0),
                              eventos: [],
                            });
                          }

                          if (row.mes_recebimento) {
                            map.get(key).eventos.push({
                              mes: row.mes_recebimento,
                              recebido: Number(row.vl_recebido_mes || 0),
                              recebido_base: Number(row.vl_recebido_base_mes || 0),
                              glosa: Number(row.vl_glosa_mes || 0),
                            });
                          }

                          return map;
                        }, new Map()).values()
                      ).map((item) => (
                        <div className="competency-card" key={`hist-${item.competencia}`}>
                          <div className="competency-card-head">
                            <div>
                              <span className="competency-label">Competência</span>
                              <strong>{item.competencia}</strong>
                              <small>{int(item.qt_contas)} conta(s)</small>
                            </div>

                            <div className="competency-summary">
                              <span>Faturado <strong>{brl(item.vl_faturado)}</strong></span>
                              <span>Recebido <strong>{brl(item.vl_recebido_base)}</strong></span>
                              <span>Glosado <strong>{brl(item.vl_glosa)}</strong></span>
                              <span>Em aberto <strong>{brl(item.vl_em_aberto)}</strong></span>
                            </div>
                          </div>

                          <div className="competency-flow">
                            <div className="competency-origin">
                              <strong>{item.competencia}</strong>
                              <small>faturado {brl(item.vl_faturado)}</small>
                            </div>

                            <div className="competency-arrow">→</div>

                            <div className="competency-events">
                              {item.eventos.length ? item.eventos.map((evento) => (
                                <div
                                  className="competency-event"
                                  key={`${item.competencia}-${evento.mes}`}
                                >
                                  <strong>{evento.mes}</strong>
                                  <span className="event-received">
                                    + {brl(evento.recebido_base)} recebido
                                  </span>
                                  {evento.glosa > 0 && (
                                    <span className="event-denied">
                                      {brl(evento.glosa)} glosado
                                    </span>
                                  )}
                                </div>
                              )) : (
                                <div className="competency-event">
                                  <strong>Sem recebimento</strong>
                                  <span>Nenhum evento financeiro localizado até agora.</span>
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="inline-note">
                            Situação atual: recebido {brl(item.vl_recebido_base)} · glosado {brl(item.vl_glosa)} · em aberto {brl(item.vl_em_aberto)}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      Nenhuma competência financeira encontrada para as contas produzidas neste período.
                    </div>
                  )}
                </Section>

                <Section title="Glosas por motivo">
                  {loading.motivos ? <div className="empty-state">Consultando motivos…</div> : motivos.length ? (
                    <div className="chart-wrap compact-chart">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={motivos} layout="vertical" margin={{ left: 12, right: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" /><XAxis type="number" />
                          <YAxis dataKey="ds_motivo_glosa" type="category" width={250} tick={{ fontSize: 11 }} />
                          <Tooltip formatter={(v) => brl(v)} /><Bar dataKey="vl_glosa" name="Valor glosado" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : <div className="empty-state">Sem motivos de glosa.</div>}
                </Section>
                <Section title="Eventos de glosa">
                  {loading.glosas ? <div className="empty-state">Consultando eventos…</div> : (
                    <DataTable
                      keyField="cd_glosas"
                      rows={glosas}
                      columns={[
                        { key: "dt_glosa", label: "Data", render: shortDate },
                        { key: "cd_reg_amb", label: "Conta" },
                        { key: "cd_atendimento", label: "Atendimento" },
                        { key: "ds_pro_fat", label: "Procedimento" },
                        { key: "ds_motivo_glosa", label: "Motivo" },
                        { key: "vl_glosa", label: "Valor", render: brl, className: "number" },
                        { key: "status_analitico", label: "Status", render: (v) => <StatusBadge value={v} /> },
                      ]}
                    />
                  )}
                </Section>
              </>
            )}

            {tab === "analises" && analisesView === "produtos" && (
              <Section title="Produtos" subtitle="Participação do uso oncológico CONVENIO_DEMO no total observado para o produto dentro do período.">
                {loading.produtos ? <div className="empty-state">Consultando produtos…</div> : (
                  <DataTable
                    keyField="cd_produto"
                    rows={produtos}
                    columns={[
                      { key: "cd_produto", label: "Código" },
                      { key: "ds_produto", label: "Produto" },
                      { key: "sn_medicamento", label: "Medicamento" },
                      { key: "mov_onco", label: "Mov. onco", render: int, className: "number" },
                      { key: "mov_total", label: "Mov. total", render: int, className: "number" },
                      { key: "pct_onco", label: "% onco", render: pct, className: "number" },
                      { key: "classificacao", label: "Classificação", render: (v) => <span className="tag">{v}</span> },
                      { key: "confianca", label: "Confiança" },
                    ]}
                  />
                )}
              </Section>
            )}

            {tab === "relatorios" && (
              <Section title="Relatórios e exportações" subtitle="PDF com layout próprio e dados estruturados para conferência no Excel.">
                <div className="report-grid">
                  <div className="report-card">
                    <div><span className="report-kicker">PDF</span><h3>Relatório executivo</h3></div>
                    <p>Resumo financeiro, recebimentos reais, competência x recebimento, glosas e produtos.</p>
                    <a className="primary-link" href={api.pdfUrl(fInicio, fFim, false)} target="_blank" rel="noreferrer">Gerar PDF executivo</a>
                  </div>
                  <div className="report-card featured">
                    <div><span className="report-kicker">PDF DETALHADO</span><h3>Conciliação e auditoria</h3></div>
                    <p>Inclui eventos de recebimento, remessas, pacientes, atendimentos e resumo de auditoria.</p>
                    <a className="primary-link" href={api.pdfUrl(fInicio, fFim, true)} target="_blank" rel="noreferrer">Gerar PDF detalhado</a>
                  </div>
                  <div className="report-card">
                    <div><span className="report-kicker">EXCEL / CSV</span><h3>Faturamento MV</h3></div>
                    <p>Faturamento por competência, item a item, agrupado por setor para conciliação com o relatório nativo.</p>
                    <a className="secondary-link" href={api.faturamentoMvCsvUrl(fInicio, fFim, setoresMv.trim())}>Exportar faturamento MV</a>
                  </div>
                  <div className="report-card">
                    <div><span className="report-kicker">EXCEL / CSV</span><h3>Pagamentos</h3></div>
                    <p>Conta, paciente, remessa, competência, recebimentos e saldo. CSV UTF-8 compatível com Excel.</p>
                    <a className="secondary-link" href={api.pagamentosCsvUrl(fInicio, fFim)}>Exportar pagamentos</a>
                  </div>
                  <div className="report-card">
                    <div><span className="report-kicker">EXCEL / CSV</span><h3>Atendimentos</h3></div>
                    <p>Rastreabilidade assistencial e financeira por conta.</p>
                    <a className="secondary-link" href={api.atendimentosCsvUrl(fInicio, fFim)}>Exportar atendimentos</a>
                  </div>
                  <div className="report-card">
                    <div><span className="report-kicker">EXCEL / CSV</span><h3>Pacientes</h3></div>
                    <p>Consolidado de faturamento, recebimento, saldo, glosa e médias.</p>
                    <a className="secondary-link" href={api.pacientesCsvUrl(fInicio, fFim)}>Exportar pacientes</a>
                  </div>
                  <div className="report-card">
                    <div><span className="report-kicker">DADOS</span><h3>XML operacional</h3></div>
                    <p>Exportação estruturada do conjunto principal.</p>
                    <a className="secondary-link" href={api.xmlUrl(fInicio, fFim)}>Exportar XML</a>
                  </div>
                </div>
              </Section>
            )}

            {tab === "admin" && session?.user?.role === "ADMIN" && <AdminUsers convenios={convenios} sessionUser={session?.user} />}

            <footer className="footer">
              <strong>TI — Hospital Demonstrativo</strong><span>Projeto de portfólio</span>
            </footer>
          </>
        ))}
      </main>
      </div>

      {selectedPatient && <div className="detail-overlay" role="dialog" aria-modal="true" aria-label="Detalhe do paciente">
        <div className="detail-drawer patient-drawer">
          <div className="detail-head"><div><span className="detail-kicker">PACIENTE</span><h2>{privacy ? `Paciente ${selectedPatient.cd_paciente}` : (selectedPatient.nm_paciente || "Paciente")}</h2><p>Código {selectedPatient.cd_paciente} · contas do período de produção selecionado</p></div><button type="button" className="icon-close" onClick={()=>setSelectedPatient(null)}>×</button></div>
          <div className="detail-metrics"><Card title="Atendimentos" value={int(selectedPatient.qt_atendimentos)} /><Card title="Contas" value={int(selectedPatient.qt_contas)} /><Card title="Faturado" value={brl(selectedPatient.vl_faturado)} /><Card title="Recebido base" value={brl(selectedPatient.vl_recebido_base)} /></div>
          <div className="detail-body"><h3>Contas e atendimentos</h3>{loading.patientAccounts ? <div className="empty-state">Consultando contas do paciente…</div> : <DataTable columns={atendCols} rows={patientAccounts} keyField="cd_reg_amb" onRowClick={(row)=>{setSelectedPatient(null);abrirConta(row);}} />}</div>
        </div>
      </div>}

      {(selectedAccount || loading.accountDetail) && <div className="detail-overlay" role="dialog" aria-modal="true" aria-label="Detalhe da conta">
        <div className="detail-drawer account-drawer">
          <div className="detail-head"><div><span className="detail-kicker">CONTA ONCOLÓGICA</span><h2>Conta {selectedAccount?.cd_reg_amb || accountDetail?.conta?.cd_reg_amb}</h2><p>{accountDetail?.conta ? `${privacy ? `Paciente ${accountDetail.conta.cd_paciente}` : accountDetail.conta.nm_paciente} · Atendimento ${accountDetail.conta.cd_atendimento}` : "Carregando identificação da conta…"}</p></div><div className="detail-head-actions">{accountDetail?.conta?.cd_reg_amb && <a className="primary-link" href={api.contaPdfUrl(accountDetail.conta.cd_reg_amb)} target="_blank" rel="noreferrer">Imprimir / PDF</a>}<button type="button" className="icon-close" onClick={()=>{setSelectedAccount(null);setAccountDetail(null);}}>×</button></div></div>
          {loading.accountDetail ? <div className="loading-panel">Carregando conta e itens…</div> : accountDetail && <>
            <div className="detail-metrics"><Card title="Faturado" value={brl(accountDetail.conta.vl_faturado)} /><Card title="Recebido base" value={brl(accountDetail.conta.vl_recebido_base)} /><Card title="Saldo" value={brl(accountDetail.conta.vl_saldo_estimado)} /><Card title="Glosa líquida" value={brl(accountDetail.conta.vl_glosa_liquida)} tone={Number(accountDetail.conta.vl_glosa_liquida)>0?"danger":""} /></div>
            <div className="account-meta"><div><span>Status</span><StatusBadge value={accountDetail.conta.status_financeiro}/></div><div><span>Remessa</span><strong>{accountDetail.conta.cd_remessa || "Sem remessa"}</strong></div><div><span>Último recebimento</span><strong>{shortDate(accountDetail.conta.ultimo_recebimento)}</strong></div><div><span>Itens</span><strong>{int(accountDetail.itens?.length)}</strong></div></div>
            <div className="detail-body"><div className="detail-section-title"><div><span className="detail-kicker">COMPOSIÇÃO</span><h3>Itens da conta</h3></div><span className="source-chip">ITREG_AMB + PRO_FAT</span></div><DataTable columns={itemCols} rows={accountDetail.itens || []} keyField="cd_lancamento" empty="Nenhum item localizado para esta conta." />
              {accountDetail.recebimentos?.length > 0 && <><h3>Recebimentos vinculados</h3><DataTable keyField="cd_reccon_rec" rows={accountDetail.recebimentos} columns={[{key:"cd_reccon_rec",label:"Evento"},{key:"dt_recebimento",label:"Data financeira",render:shortDate},{key:"vl_recebido_base",label:"Recebido base",render:brl,className:"number"},{key:"vl_acrescimo",label:"Acréscimo",render:brl,className:"number"},{key:"vl_glosa",label:"Glosa",render:brl,className:"number"}]} /></>}
              {accountDetail.glosas?.length > 0 && <><h3>Glosas da conta</h3><DataTable keyField="cd_glosas" rows={accountDetail.glosas} columns={[{key:"dt_glosa",label:"Data",render:shortDate},{key:"ds_pro_fat",label:"Procedimento"},{key:"ds_motivo_glosa",label:"Motivo"},{key:"vl_glosa",label:"Valor",render:brl,className:"number"}]} /></>}
            </div>
          </>}
        </div>
      </div>}
    </div>
  );
}
