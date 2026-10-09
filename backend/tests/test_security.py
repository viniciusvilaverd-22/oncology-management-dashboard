from app.auth.security import hash_password, verify_password, new_token, token_hash

def test_password_hash_roundtrip():
    password = "Senha-Demo-Segura-123!"
    encoded = hash_password(password)

    assert encoded != password
    assert verify_password(password, encoded)
    assert not verify_password("senha-incorreta", encoded)

def test_tokens_are_random():
    a = new_token()
    b = new_token()

    assert a
    assert b
    assert a != b

def test_token_hash_is_deterministic():
    token = "token-demo"

    assert token_hash(token) == token_hash(token)
    assert token_hash(token) != token
