"""OIDC-protected proxy in front of the Microsoft playwright-mcp server.

A FastMCP `OIDCProxy` enforces authentication against any standards-compliant
OpenID Connect provider, and `create_proxy` forwards every MCP call to the
upstream playwright-mcp container.
"""

import uvicorn
from fastmcp.server import create_proxy
from fastmcp.server.auth.oidc_proxy import OIDCProxy

from .config import settings


auth = OIDCProxy(
    config_url=f"{settings.auth_server_url}/.well-known/openid-configuration",
    client_id=settings.client_id,
    client_secret=settings.client_secret,
    base_url=settings.own_server_url,
    token_endpoint_auth_method="client_secret_post",
    required_scopes=settings.required_scopes,
    audience=settings.audience or None,
)


proxy = create_proxy(
    settings.upstream_mcp_url,
    name="Playwright (OIDC-protected)",
    auth=auth,
)


app = proxy.http_app(path="/mcp", transport="streamable-http", stateless_http=True)


def main() -> None:
    uvicorn.run(app, host=settings.server_host, port=settings.server_port)


if __name__ == "__main__":
    main()
