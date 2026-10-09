from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from app.auth.store import get_session

COOKIE_NAME = 'oncology_session'
CSRF_COOKIE = 'oncology_csrf'


def require_user(oncology_session: str | None = Cookie(default=None, alias=COOKIE_NAME)) -> dict:
    if not oncology_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Sessão não autenticada.')
    session = get_session(oncology_session)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Sessão expirada ou inválida.')
    return session[0]


def require_admin(user: dict = Depends(require_user)) -> dict:
    if user.get('role') != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Acesso restrito a administradores.')
    return user


def require_csrf(
    request: Request,
    user: dict = Depends(require_user),
    oncology_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
    oncology_csrf: str | None = Cookie(default=None, alias=CSRF_COOKIE),
    x_csrf_token: str | None = Header(default=None, alias='X-CSRF-Token'),
) -> dict:
    session = get_session(oncology_session or '')
    if not session or not oncology_csrf or not x_csrf_token or oncology_csrf != x_csrf_token or session[1] != x_csrf_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Proteção CSRF inválida.')
    return user


def selected_convenio(
    user: dict = Depends(require_user),
    x_convenio_id: int = Header(default=11, alias='X-Convenio-Id'),
) -> int:
    if not user.get('all_convenios') and x_convenio_id not in set(user.get('convenios') or []):
        raise HTTPException(status_code=403, detail='Usuário sem permissão para este convênio.')
    return x_convenio_id


def require_onco_model(cd_convenio: int = Depends(selected_convenio)) -> int:
    if cd_convenio != 11:
        raise HTTPException(
            status_code=409,
            detail='Convênio autorizado, porém o modelo oncológico/financeiro deste convênio ainda não foi homologado. CONVENIO_DEMO (11) permanece como modelo validado.',
        )
    return cd_convenio


def require_operational(user: dict = Depends(require_user)) -> dict:
    if user.get('role') not in {'ADMIN', 'FATURAMENTO', 'AUDITORIA'}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Seu perfil possui acesso apenas à visão executiva.')
    return user
