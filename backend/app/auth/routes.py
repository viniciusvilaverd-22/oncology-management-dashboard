from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app.auth.deps import COOKIE_NAME, CSRF_COOKIE, require_admin, require_csrf, require_user
from app.auth.store import authenticate, create_session, create_user, delete_session, list_users, update_user, change_password, log_event, list_audit_events, get_user, count_active_admins
from app.config import settings
from app.integrations.registry import get_adapter

router = APIRouter(prefix='/api/auth', tags=['Autenticação'])

class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=1, max_length=256)

class PasswordChangeIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=12, max_length=256)

class UserCreateIn(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    display_name: str = Field(min_length=2, max_length=160)
    email: str | None = Field(default=None, max_length=240)
    password: str = Field(min_length=12, max_length=256)
    role: str
    all_convenios: bool = False
    convenios: list[int] = []
    default_convenio: int | None = None
    must_change_password: bool = True

class UserUpdateIn(BaseModel):
    display_name: str | None = Field(default=None, max_length=160)
    email: str | None = Field(default=None, max_length=240)
    password: str | None = Field(default=None, max_length=256)
    role: str | None = None
    active: bool | None = None
    all_convenios: bool | None = None
    convenios: list[int] | None = None
    default_convenio: int | None = None
    must_change_password: bool | None = None


def public_user(user: dict) -> dict:
    return {k: v for k, v in user.items() if k not in {'password_hash'}}

@router.post('/login')
def login(payload: LoginIn, response: Response, request: Request):
    user = authenticate(payload.username, payload.password)
    if not user:
        log_event('LOGIN_FAILED', details=f'username={payload.username.strip().lower()}', remote_addr=request.client.host if request.client else None)
        raise HTTPException(status_code=401, detail='Usuário ou senha inválidos.')
    token, csrf, expires = create_session(user['id'])
    cookie_args = dict(httponly=True, secure=settings.app_secure_cookies, samesite='strict', path='/', max_age=settings.session_hours * 3600)
    response.set_cookie(COOKIE_NAME, token, **cookie_args)
    response.set_cookie(CSRF_COOKIE, csrf, httponly=False, secure=settings.app_secure_cookies, samesite='strict', path='/', max_age=settings.session_hours * 3600)
    log_event('LOGIN_OK', actor=user, remote_addr=request.client.host if request.client else None)
    return {'user': public_user(user), 'csrf_token': csrf, 'expires_at': expires}

@router.post('/logout')
def logout(response: Response, request: Request, user: dict = Depends(require_csrf)):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        delete_session(token)
    log_event('LOGOUT', actor=user, remote_addr=request.client.host if request.client else None)
    response.delete_cookie(COOKIE_NAME, path='/')
    response.delete_cookie(CSRF_COOKIE, path='/')
    return {'status': 'ok'}

@router.get('/me')
def me(request: Request, user: dict = Depends(require_user)):
    csrf = request.cookies.get(CSRF_COOKIE)
    return {'user': public_user(user), 'csrf_token': csrf}

@router.get('/convenios')
def convenios(user: dict = Depends(require_user)):
    rows = get_adapter().list_payers()
    allowed = None if user.get('all_convenios') else set(user.get('convenios') or [])
    out = []
    for row in rows:
        payer_id = int(row.get('payer_id'))
        if allowed is not None and payer_id not in allowed:
            continue
        out.append({
            'payer_id': payer_id,
            'payer_name': row.get('payer_name'),
            'modelo_homologado': bool(row.get('supported', False)),
            'modelo': row.get('model_name') or 'PRIVATE_ADAPTER',
        })
    return out

@router.get('/users')
def users(user: dict = Depends(require_admin)):
    return [public_user(x) for x in list_users()]

@router.post('/users')
def users_create(payload: UserCreateIn, request: Request, user: dict = Depends(require_admin), csrf_user: dict = Depends(require_csrf)):
    try:
        created = create_user(**payload.model_dump())
        log_event('USER_CREATED', actor=user, target_user_id=created['id'], details=f"role={created['role']}", remote_addr=request.client.host if request.client else None)
        return public_user(created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch('/users/{user_id}')
def users_update(user_id: int, payload: UserUpdateIn, request: Request, user: dict = Depends(require_admin), csrf_user: dict = Depends(require_csrf)):
    try:
        data = payload.model_dump(exclude_unset=True)
        target = get_user(user_id)
        if not target:
            raise ValueError('Usuário não encontrado.')
        if user_id == user['id'] and data.get('active') is False:
            raise ValueError('Você não pode bloquear sua própria conta. Use outro administrador.')
        losing_admin = target.get('role') == 'ADMIN' and target.get('active') and (data.get('active') is False or (data.get('role') is not None and str(data.get('role')).upper() != 'ADMIN'))
        if losing_admin and count_active_admins() <= 1:
            raise ValueError('Não é permitido bloquear ou remover o perfil do último administrador ativo.')
        updated = update_user(user_id, **data)
        log_event('USER_UPDATED', actor=user, target_user_id=user_id, details=','.join(sorted(data.keys())), remote_addr=request.client.host if request.client else None)
        return public_user(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/change-password')
def password_change(payload: PasswordChangeIn, request: Request, user: dict = Depends(require_csrf)):
    try:
        updated = change_password(user['id'], payload.current_password, payload.new_password)
        log_event('PASSWORD_CHANGED', actor=user, target_user_id=user['id'], remote_addr=request.client.host if request.client else None)
        return {'status': 'ok', 'user': public_user(updated), 'reauth_required': True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/audit-log')
def audit_log(limit: int = 200, user: dict = Depends(require_admin)):
    return list_audit_events(limit)
