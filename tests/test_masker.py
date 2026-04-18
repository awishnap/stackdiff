"""Tests for stackdiff.masker."""

from stackdiff.masker import is_sensitive, mask_config, MASK_PLACEHOLDER


def test_is_sensitive_password():
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_secret():
    assert is_sensitive("APP_SECRET") is True


def test_is_sensitive_token():
    assert is_sensitive("ACCESS_TOKEN") is True


def test_is_sensitive_api_key():
    assert is_sensitive("API_KEY") is True
    assert is_sensitive("STRIPE_APIKEY") is True


def test_is_sensitive_case_insensitive():
    assert is_sensitive("db_password") is True
    assert is_sensitive("Auth_Token") is True


def test_is_not_sensitive():
    assert is_sensitive("HOST") is False
    assert is_sensitive("PORT") is False
    assert is_sensitive("APP_NAME") is False


def test_mask_config_replaces_sensitive():
    config = {"DB_PASSWORD": "s3cr3t", "HOST": "localhost"}
    masked = mask_config(config)
    assert masked["DB_PASSWORD"] == MASK_PLACEHOLDER
    assert masked["HOST"] == "localhost"


def test_mask_config_does_not_mutate_original():
    config = {"DB_PASSWORD": "s3cr3t"}
    mask_config(config)
    assert config["DB_PASSWORD"] == "s3cr3t"


def test_mask_config_extra_patterns():
    config = {"STRIPE_PK": "pk_live_xxx", "HOST": "localhost"}
    masked = mask_config(config, extra_patterns=[r"(?i)stripe"])
    assert masked["STRIPE_PK"] == MASK_PLACEHOLDER
    assert masked["HOST"] == "localhost"


def test_mask_config_empty():
    assert mask_config({}) == {}
