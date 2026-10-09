from app.auth.store import (
    authenticate,
    change_password,
    create_session,
    create_user,
    get_session,
    init_auth_db,
)
from app.config import settings


def test_user_authentication_session_and_password_rotation(tmp_path, monkeypatch):
    db_path = tmp_path / "auth.db"
    monkeypatch.setattr(settings, "auth_db_path", str(db_path))

    init_auth_db()

    user = create_user(
        username="portfolio_test",
        display_name="Portfolio Test",
        password="Senha-Demo-Segura-123!",
        role="ADMIN",
        all_convenios=True,
        must_change_password=False,
    )

    authenticated = authenticate("portfolio_test", "Senha-Demo-Segura-123!")
    assert authenticated
    assert authenticated["id"] == user["id"]
    assert authenticate("portfolio_test", "senha-incorreta") is None

    token, csrf, expires_at = create_session(user["id"])
    session = get_session(token)

    assert token
    assert csrf
    assert expires_at
    assert session
    assert session[0]["id"] == user["id"]
    assert session[1] == csrf

    change_password(
        user["id"],
        "Senha-Demo-Segura-123!",
        "Nova-Senha-Demo-456!",
    )

    assert authenticate("portfolio_test", "Senha-Demo-Segura-123!") is None
    assert authenticate("portfolio_test", "Nova-Senha-Demo-456!")
    assert get_session(token) is None
