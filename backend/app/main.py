import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.auth import init_auth_db
from app.auth.routes import router as auth_router
from app.config import settings
from app.api.routes import router as onco_router

app = FastAPI(
    title=settings.app_name,
    version='0.6.3.1',
    description='Gestão integrada read-only para oncologia, faturamento, recebimentos, glosas e auditoria no Hospital ERP',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5174', 'http://localhost:5174'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PATCH'],
    allow_headers=['Content-Type', 'X-CSRF-Token', 'X-Convenio-Id'],
)

_audit = logging.getLogger('oncology_dashboard.audit')

@app.on_event('startup')
def startup():
    init_auth_db()

@app.middleware('http')
async def audit_access(request: Request, call_next):
    started = perf_counter()
    request_id = request.headers.get('X-Request-ID') or uuid4().hex
    response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    if request.url.path.startswith('/api/'):
        client = request.client.host if request.client else '-'
        elapsed_ms = round((perf_counter() - started) * 1000, 1)
        _audit.info(
            'access request_id=%s client=%s path=%s method=%s status=%s elapsed_ms=%s',
            request_id,
            client,
            request.url.path,
            request.method,
            response.status_code,
            elapsed_ms,
        )
    return response

@app.get('/health')
def health():
    return {'status': 'ok', 'service': settings.app_name, 'mode': 'read-only-oracle', 'version': '0.6.3.1', 'auth': 'enabled'}

@app.get('/db-health')
def db_health():
    from app.db.oracle import fetch_one
    row = fetch_one('SELECT 1 AS OK FROM DUAL', {})
    return {'status': 'ok', 'database': 'oracle', 'result': row}

app.include_router(auth_router)
app.include_router(onco_router)
