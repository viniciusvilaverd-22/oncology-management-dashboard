import os
from pathlib import Path
import glob
import oracledb
from contextlib import contextmanager
from app.config import settings

_pool = None
_client_initialized = False

def _find_oracle_client():
    candidates = []

    env_dir = os.getenv("ORACLE_CLIENT_LIB_DIR")
    if env_dir:
        candidates.append(Path(env_dir))

    env_home = os.getenv("ORACLE_HOME")
    if env_home:
        candidates.append(Path(env_home))

    for pattern in (
        "/opt/oracle/instantclient_*",
        "/usr/lib/oracle/*/client64/lib",
        "/usr/lib/oracle/*/client/lib",
    ):
        for p in glob.glob(pattern):
            candidates.append(Path(p))

    for p in candidates:
        if (p / "libclntsh.so").exists() or list(p.glob("libclntsh.so.*")):
            return p

    raise RuntimeError(
        "Oracle Instant Client não encontrado. "
        "Defina ORACLE_CLIENT_LIB_DIR ou instale em /opt/oracle/instantclient_*."
    )

def _init_oracle_client():
    global _client_initialized
    if _client_initialized:
        return

    lib_dir = _find_oracle_client()
    oracledb.init_oracle_client(lib_dir=str(lib_dir))
    _client_initialized = True

def init_pool():
    global _pool
    if _pool is None:
        _init_oracle_client()
        _pool = oracledb.create_pool(
            user=settings.oracle_user,
            password=settings.oracle_password,
            dsn=settings.oracle_dsn,
            min=1,
            max=2,
            increment=1,
            timeout=60,
        )
    return _pool

@contextmanager
def get_connection():
    pool = init_pool()
    conn = pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)

def fetch_all(sql: str, binds: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, binds)
            cols = [d[0].lower() for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

def fetch_one(sql: str, binds: dict):
    rows = fetch_all(sql, binds)
    return rows[0] if rows else None