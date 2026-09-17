import pytest

from agentgate.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_safe_defaults_load_without_environment(monkeypatch):
    for name in (
        "AGENTGATE_ENV",
        "AZURE_AI_PROJECT_ENDPOINT",
        "AZURE_AI_MODEL_DEPLOYMENT_NAME",
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = get_settings()

    assert settings.environment == "development"
    assert settings.azure_ai_project_endpoint is None
    assert settings.azure_ai_model_deployment_name is None
    assert settings.applicationinsights_connection_string is None


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv("AGENTGATE_ENV", "test")
    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "test-model")
    monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "test-connection")

    settings = get_settings()

    assert settings.environment == "test"
    assert settings.azure_ai_project_endpoint == "https://example.invalid"
    assert settings.azure_ai_model_deployment_name == "test-model"
    assert settings.applicationinsights_connection_string.get_secret_value() == (
        "test-connection"
    )