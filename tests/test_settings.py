import pytest
from pydantic import ValidationError

from utils.settings import Settings

# `_env_file=None` keeps a developer's local .env out of the assertions.


def test_openai_api_key_is_required(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_openai_api_key_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
    settings = Settings(_env_file=None)
    assert settings.openai_api_key.get_secret_value() == "sk-test-123"


def test_api_key_never_leaks_in_logs_or_repr(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-super-secret")
    settings = Settings(_env_file=None)

    assert "sk-super-secret" not in repr(settings)
    assert "sk-super-secret" not in str(settings)
    assert str(settings.openai_api_key) == "*" * 10


def test_unknown_environment_variables_are_ignored(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
    monkeypatch.setenv("SOME_UNRELATED_SETTING", "whatever")

    # extra="ignore" means stray vars must not raise.
    assert Settings(_env_file=None).openai_api_key is not None
