import React, { useEffect, useState } from "react";
import App from "./App.jsx";
import { authApi } from "./authApi.js";

const BASE = import.meta.env.BASE_URL || "/";

function Logo({ compact = false }) {
  return <img className={compact ? "institution-logo compact" : "institution-logo"} src={`${BASE}hospital-demo-logo.svg`} alt="Hospital Demonstrativo" />;
}

function Login({ onAuthenticated }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true); setError("");
    try { onAuthenticated(await authApi.login(username, password)); }
    catch (err) { setError(err.message || "Não foi possível entrar."); }
    finally { setLoading(false); }
  }

  return (
    <div className="login-page">
      <div className="login-brand-panel">
        <div className="logo-stage"><Logo /></div>
        <div className="login-brand-copy">
          <span className="login-kicker">SISTEMA INSTITUCIONAL</span>
          <h1>Gestão Integrada da Oncologia</h1>
          <p>Produção, faturamento, recebimentos, glosas e rastreabilidade em uma experiência única.</p>
          <div className="brand-lines"><span></span><span></span><span></span></div>
        </div>
        <div className="login-trust-grid">
          <div><strong>Leitura executiva</strong><small>Informação simples sem perder rastreabilidade.</small></div>
          <div><strong>Acesso por perfil</strong><small>Cada usuário vê somente o que precisa.</small></div>
          <div><strong>Multi-convênio</strong><small>Estrutura pronta para expansão controlada.</small></div>
        </div>
      </div>
      <div className="login-form-panel">
        <form className="login-card" onSubmit={submit}>
          <div className="mobile-logo"><Logo compact /></div>
          <span className="login-kicker">ACESSO SEGURO</span>
          <h2>Bem-vindo(a)</h2>
          <p>Entre com seu usuário institucional para acessar o painel.</p>
          <label>Usuário<input autoFocus autoComplete="username" value={username} onChange={(e)=>setUsername(e.target.value)} placeholder="Usuário" /></label>
          <label>Senha<input type="password" autoComplete="current-password" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="Senha" /></label>
          {error && <div className="login-error">{error}</div>}
          <button className="login-button" disabled={loading || !username || !password}>{loading ? "Entrando…" : "Entrar"}</button>
          <div className="login-note">Acesso restrito. As consultas ao Hospital ERP permanecem em modo read-only.</div>
        </form>
      </div>
    </div>
  );
}

export default function Root() {
  const [session, setSession] = useState(null);
  const [checking, setChecking] = useState(true);
  const [convenios, setConvenios] = useState([]);
  const [convenio, setConvenio] = useState(null);

  useEffect(() => {
    authApi.me().then(setSession).catch(()=>setSession(null)).finally(()=>setChecking(false));
  }, []);

  useEffect(() => {
    if (!session?.user) return;
    authApi.convenios().then((rows) => {
      setConvenios(rows || []);
      const saved = Number(localStorage.getItem("oncology_convenio") || 11);
      const selected = rows?.find((x)=>x.cd_convenio===saved) || rows?.find((x)=>x.cd_convenio===11) || rows?.[0] || null;
      setConvenio(selected);
    }).catch(()=>setConvenios([]));
  }, [session]);

  async function logout() {
    try { await authApi.logout(); } catch {}
    setSession(null); setConvenios([]); setConvenio(null);
  }

  function selectConvenio(cd) {
    const item = convenios.find((x)=>String(x.cd_convenio)===String(cd));
    if (item) { setConvenio(item); localStorage.setItem("oncology_convenio", String(item.cd_convenio)); }
  }

  if (checking) return <div className="boot-screen">Carregando acesso…</div>;
  if (!session?.user) return <Login onAuthenticated={setSession} />;
  return <App session={session} convenios={convenios} convenio={convenio} onConvenioChange={selectConvenio} onLogout={logout} />;
}
