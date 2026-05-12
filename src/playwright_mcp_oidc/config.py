from pydantic import Field
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

    @property
    def required_scopes(self) -> list[str]:
        return [s.strip() for s in self.required_scopes_raw.split(",") if s.strip()]


settings = Settings()  # type: ignore[call-arg]
