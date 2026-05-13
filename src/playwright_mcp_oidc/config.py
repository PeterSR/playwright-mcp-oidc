from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    own_server_url: str = Field(alias="OWN_SERVER_URL")
    auth_server_url: str = Field(alias="AUTH_SERVER_URL")
    client_id: str = Field(alias="CLIENT_ID", default="playwright-mcp-server")
    client_secret: str = Field(alias="CLIENT_SECRET")
    required_scopes_raw: str = Field(alias="REQUIRED_SCOPES", default="profile,email")
    audience: str = Field(alias="AUDIENCE", default="")

    upstream_mcp_url: str = Field(
        alias="UPSTREAM_MCP_URL", default="http://playwright:8931/mcp"
    )

    server_host: str = Field(alias="SERVER_HOST", default="0.0.0.0")
    server_port: int = Field(alias="SERVER_PORT", default=8929)

    machine_api_key: str | None = Field(alias="MACHINE_API_KEY", default=None)

    @field_validator("machine_api_key")
    @classmethod
    def _validate_machine_api_key(cls, v: str | None) -> str | None:
        # Empty/None disables the machine-key auth path entirely.
        if not v:
            return None
        if len(v) < 32:
            raise ValueError(
                "MACHINE_API_KEY must be at least 32 characters when set. "
                "Generate one with: openssl rand -base64 32"
            )
        return v

    @property
    def required_scopes(self) -> list[str]:
        return [s.strip() for s in self.required_scopes_raw.split(",") if s.strip()]


settings = Settings()  # type: ignore[call-arg]
