import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from app.config import settings
from app.auth.security import hash_password, new_token, token_hash, utcnow_iso, verify_password

ROLES = {'ADMIN', 'FATURAMENTO', 'AUDITORIA', 'VISUALIZACAO'}


def _db_path() -> Path:
    p = Path(settings.auth_db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


@contextmanager
def conn():
    db = sqlite3.connect(_db_path(), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA journal_mode=WAL')
    try:
        yield db
        db.commit()
    finally:
        db.close()


def init_auth_db():
    with conn() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            display_name TEXT NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            all_convenios INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login_at TEXT
        );
        CREATE TABLE IF NOT EXISTS user_convenios (
            user_id INTEGER NOT NULL,
            payer_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, payer_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            csrf_token TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_exp ON sessions(expires_at);
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            occurred_at TEXT NOT NULL,
            actor_user_id INTEGER,
            actor_username TEXT,
            event_type TEXT NOT NULL,
            target_user_id INTEGER,
            details TEXT,
            remote_addr TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_audit_events_time ON audit_events(occurred_at DESC);
        ''')
        # Migrações aditivas para instalações V6 existentes.
        cols = {r['name'] for r in db.execute('PRAGMA table_info(users)')}
        if 'default_convenio' not in cols:
            db.execute('ALTER TABLE users ADD COLUMN default_convenio INTEGER')
        if 'must_change_password' not in cols:
            db.execute('ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0')
        if 'last_password_change_at' not in cols:
            db.execute('ALTER TABLE users ADD COLUMN last_password_change_at TEXT')


def normalize_username(value: str) -> str:
    return value.strip().lower()


def create_user(username: str, display_name: str, password: str, role: str, email: str | None = None,
                all_convenios: bool = False, convenios: Iterable[int] | None = None,
                default_convenio: int | None = None, must_change_password: bool = True) -> dict:
    username = normalize_username(username)
    role = role.strip().upper()
    if len(username) < 3:
        raise ValueError('Usuário deve ter pelo menos 3 caracteres.')
    if len(display_name.strip()) < 2:
        raise ValueError('Nome deve ter pelo menos 2 caracteres.')
    if len(password) < 12:
        raise ValueError('A senha deve ter pelo menos 12 caracteres.')
    if role not in ROLES:
        raise ValueError('Perfil de acesso inválido.')
    now = utcnow_iso()
    try:
        with conn() as db:
            cur = db.execute(
                'INSERT INTO users(username,display_name,email,password_hash,role,active,all_convenios,created_at,updated_at,default_convenio,must_change_password,last_password_change_at) VALUES(?,?,?,?,?,1,?,?,?,?,?,?)',
                (username, display_name.strip(), (email or '').strip() or None, hash_password(password), role, 1 if all_convenios else 0, now, now, default_convenio, 1 if must_change_password else 0, now),
            )
            user_id = cur.lastrowid
            for cd in sorted({int(x) for x in (convenios or [])}):
                db.execute('INSERT OR IGNORE INTO user_convenios(user_id,payer_id) VALUES(?,?)', (user_id, cd))
    except sqlite3.IntegrityError as e:
        raise ValueError('Já existe um usuário com este login.') from e
    return get_user(user_id)


def get_user(user_id: int) -> dict | None:
    with conn() as db:
        row = db.execute('SELECT id,username,display_name,email,role,active,all_convenios,created_at,updated_at,last_login_at,default_convenio,must_change_password,last_password_change_at FROM users WHERE id=?', (user_id,)).fetchone()
        if not row:
            return None
        conv = [r['payer_id'] for r in db.execute('SELECT payer_id FROM user_convenios WHERE user_id=? ORDER BY payer_id', (user_id,))]
    data = dict(row)
    data['active'] = bool(data['active'])
    data['all_convenios'] = bool(data['all_convenios'])
    data['must_change_password'] = bool(data.get('must_change_password'))
    data['convenios'] = conv
    return data


def list_users() -> list[dict]:
    with conn() as db:
        ids = [r['id'] for r in db.execute('SELECT id FROM users ORDER BY display_name, username')]
    return [get_user(i) for i in ids]


def update_user(user_id: int, *, display_name: str | None = None, email: str | None = None,
                role: str | None = None, active: bool | None = None, all_convenios: bool | None = None,
                convenios: Iterable[int] | None = None, password: str | None = None,
                default_convenio: int | None = None, must_change_password: bool | None = None) -> dict:
    current = get_user(user_id)
    if not current:
        raise ValueError('Usuário não encontrado.')
    changes = []
    params = []
    if display_name is not None:
        changes.append('display_name=?'); params.append(display_name.strip())
    if email is not None:
        changes.append('email=?'); params.append(email.strip() or None)
    if role is not None:
        role = role.strip().upper()
        if role not in ROLES: raise ValueError('Perfil de acesso inválido.')
        changes.append('role=?'); params.append(role)
    if active is not None:
        changes.append('active=?'); params.append(1 if active else 0)
    if all_convenios is not None:
        changes.append('all_convenios=?'); params.append(1 if all_convenios else 0)
    if default_convenio is not None:
        changes.append('default_convenio=?'); params.append(int(default_convenio))
    if must_change_password is not None:
        changes.append('must_change_password=?'); params.append(1 if must_change_password else 0)
    if password:
        if len(password) < 12: raise ValueError('A senha deve ter pelo menos 12 caracteres.')
        changes.append('password_hash=?'); params.append(hash_password(password))
        changes.append('last_password_change_at=?'); params.append(utcnow_iso())
    changes.append('updated_at=?'); params.append(utcnow_iso())
    params.append(user_id)
    with conn() as db:
        db.execute(f"UPDATE users SET {', '.join(changes)} WHERE id=?", params)
        if convenios is not None:
            db.execute('DELETE FROM user_convenios WHERE user_id=?', (user_id,))
            for cd in sorted({int(x) for x in convenios}):
                db.execute('INSERT INTO user_convenios(user_id,payer_id) VALUES(?,?)', (user_id, cd))
        if active is False:
            db.execute('DELETE FROM sessions WHERE user_id=?', (user_id,))
    return get_user(user_id)



def count_active_admins() -> int:
    with conn() as db:
        row = db.execute("SELECT COUNT(*) AS n FROM users WHERE active=1 AND role='ADMIN'").fetchone()
        return int(row['n'] if row else 0)

def authenticate(username: str, password: str) -> dict | None:
    with conn() as db:
        row = db.execute('SELECT id,password_hash,active FROM users WHERE username=? COLLATE NOCASE', (normalize_username(username),)).fetchone()
        if not row or not row['active'] or not verify_password(password, row['password_hash']):
            return None
        db.execute('UPDATE users SET last_login_at=?, updated_at=updated_at WHERE id=?', (utcnow_iso(), row['id']))
        user_id = row['id']
    return get_user(user_id)


def create_session(user_id: int) -> tuple[str, str, str]:
    session_token = new_token()
    csrf = new_token()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=settings.session_hours)
    with conn() as db:
        db.execute('DELETE FROM sessions WHERE expires_at < ?', (now.isoformat(),))
        db.execute(
            'INSERT INTO sessions(token_hash,user_id,csrf_token,created_at,expires_at,last_seen_at) VALUES(?,?,?,?,?,?)',
            (token_hash(session_token), user_id, csrf, now.isoformat(), expires.isoformat(), now.isoformat()),
        )
    return session_token, csrf, expires.isoformat()


def get_session(session_token: str) -> tuple[dict, str] | None:
    now = datetime.now(timezone.utc)
    with conn() as db:
        row = db.execute('SELECT user_id,csrf_token,expires_at FROM sessions WHERE token_hash=?', (token_hash(session_token),)).fetchone()
        if not row:
            return None
        if datetime.fromisoformat(row['expires_at']) <= now:
            db.execute('DELETE FROM sessions WHERE token_hash=?', (token_hash(session_token),))
            return None
        db.execute('UPDATE sessions SET last_seen_at=? WHERE token_hash=?', (now.isoformat(), token_hash(session_token)))
        user_id, csrf = row['user_id'], row['csrf_token']
    user = get_user(user_id)
    if not user or not user['active']:
        return None
    return user, csrf


def delete_session(session_token: str):
    with conn() as db:
        db.execute('DELETE FROM sessions WHERE token_hash=?', (token_hash(session_token),))


def change_password(user_id: int, current_password: str, new_password: str) -> dict:
    if len(new_password) < 12:
        raise ValueError('A nova senha deve ter pelo menos 12 caracteres.')
    with conn() as db:
        row = db.execute('SELECT password_hash FROM users WHERE id=?', (user_id,)).fetchone()
        if not row or not verify_password(current_password, row['password_hash']):
            raise ValueError('Senha atual inválida.')
        now = utcnow_iso()
        db.execute('UPDATE users SET password_hash=?, must_change_password=0, last_password_change_at=?, updated_at=? WHERE id=?',
                   (hash_password(new_password), now, now, user_id))
        db.execute('DELETE FROM sessions WHERE user_id=?', (user_id,))
    return get_user(user_id)

def log_event(event_type: str, *, actor: dict | None = None, target_user_id: int | None = None, details: str | None = None, remote_addr: str | None = None):
    with conn() as db:
        db.execute('INSERT INTO audit_events(occurred_at,actor_user_id,actor_username,event_type,target_user_id,details,remote_addr) VALUES(?,?,?,?,?,?,?)',
                   (utcnow_iso(), actor.get('id') if actor else None, actor.get('username') if actor else None, event_type, target_user_id, details, remote_addr))

def list_audit_events(limit: int = 200) -> list[dict]:
    limit = max(1, min(int(limit), 500))
    with conn() as db:
        rows = db.execute('SELECT id,occurred_at,actor_user_id,actor_username,event_type,target_user_id,details,remote_addr FROM audit_events ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    return [dict(r) for r in rows]
