from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	environment: Literal["development", "test", "production"] = Field(
		default="development",
		validation_alias="AGENTGATE_ENV",
	)
	azure_ai_project_endpoint: str | None = Field(
		default=None,
		validation_alias="AZURE_AI_PROJECT_ENDPOINT",
	)
	azure_ai_model_deployment_name: str | None = Field(
		default=None,
		validation_alias="AZURE_AI_MODEL_DEPLOYMENT_NAME",
	)
	applicationinsights_connection_string: SecretStr | None = Field(
		default=None,
		validation_alias="APPLICATIONINSIGHTS_CONNECTION_STRING",
	)

	model_config = SettingsConfigDict(
		env_file=".env",
		extra="ignore",
	)


@lru_cache
def get_settings() -> Settings:
	return Settings()
