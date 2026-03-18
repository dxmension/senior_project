from nutrack.auth.security import JWTService


def test_access_token_round_trip_keeps_access_type() -> None:
    service = JWTService()

    token = service.create_access_token(5)
    payload = service.decode_access_token(token)

    assert payload["sub"] == "5"
    assert payload["type"] == "access"
    assert payload["jti"]


def test_refresh_token_round_trip_keeps_refresh_type() -> None:
    service = JWTService()

    token, jti = service.create_refresh_token(6)
    payload = service.decode_refresh_token(token)

    assert payload["sub"] == "6"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti


def test_decode_access_token_rejects_refresh_token() -> None:
    service = JWTService()

    token, _ = service.create_refresh_token(7)

    assert service.decode_access_token(token) == {}

