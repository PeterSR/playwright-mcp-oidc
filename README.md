# playwright-mcp-oidc

**Run browser automation as a service for your LLM agents — once, securely,
for every client.**

Microsoft's [Playwright MCP](https://github.com/microsoft/playwright-mcp)
gives any MCP-aware agent (Claude Code, Codex, Cursor, your own scripts…)
a real headless browser to drive: navigate pages, click, type, screenshot,
extract structured data. It's powerful, but the upstream image ships with
**no authentication** — it expects to live on `localhost`, behind a VPN,
or inside trusted infra. That makes it awkward to share: every project,
every machine, every teammate ends up running their own copy.

This repo solves that. It wraps the upstream image in a tiny FastMCP proxy
that enforces **OpenID Connect** on every request, so you can:

- 🌐 **Host it once, publicly.** Put `playwright-mcp.yourdomain.com` on the
  internet behind your existing IdP — no VPN, no SSH tunnel, no per-project
  setup.
- 🔑 **Reuse your identity provider.** Authelia, Keycloak, Authentik, Auth0,
  Okta, Google — anything that speaks OpenID Connect Discovery works.
- 🤝 **One config snippet per client.** Any MCP client that supports HTTP
  transport + OAuth (Claude Code does, out of the box) connects with a
  three-line config block. Tokens cache locally; subsequent runs are
  silent.
- 🪶 **Tiny, stateless, boring.** Two containers, ~80 lines of Python, no
  database. Restart freely. The proxy adds auth and gets out of the way —
  every MCP tool, resource, and prompt from the upstream image is
  forwarded verbatim.

## Architecture

```
MCP Client (e.g. Claude Code)
   │   OAuth (MCP spec) ──────►  Your OIDC IdP
   ▼
[ playwright-mcp-proxy ]   FastMCP + OIDCProxy   :8929
   │
   ▼  http://playwright:8931/mcp   (internal docker network)
[ playwright-mcp-upstream ]   mcr.microsoft.com/playwright/mcp   (headless chromium)
```

Two containers share a private docker network (`playwright-mcp-net`). The
upstream Playwright server is **not** published — only the OIDC-protected
proxy is reachable from the outside, so unauthenticated traffic never
reaches the browser.

## Compatibility

Works with any identity provider that implements **OpenID Connect
Discovery 1.0** (a `/.well-known/openid-configuration` endpoint) and
either:

- supports **dynamic client registration**, or
- lets you **manually register a confidential client** with
  `client_secret_post` token endpoint auth.

Known-compatible providers include Authelia, Keycloak, Authentik, Auth0,
Okta, Google, and any other standards-compliant OIDC implementation.

## Deploying

1. **Register an OAuth client in your IdP.** The shape:
   - **Client type**: confidential
   - **Client ID**: `playwright-mcp-server` (or whatever you put in `CLIENT_ID`)
   - **Client secret**: any strong secret — copy it into `CLIENT_SECRET`
   - **Redirect URI**: `${OWN_SERVER_URL}/auth/callback`
   - **Grant types**: Authorization Code (with PKCE)
   - **Scopes**: `openid`, `profile`, `email`
   - **Token endpoint auth method**: `client_secret_post`
2. **DNS + TLS.** Point the public hostname (e.g.
   `playwright-mcp.example.com`) at the host running this stack and let a
   reverse proxy (Cloudflare Tunnel, Traefik, Caddy, nginx, …) terminate
   TLS and forward to port `8929`.
3. **Configure environment.** Copy `.env.example` to `.env` and fill in at
   least `OWN_SERVER_URL`, `AUTH_SERVER_URL`, and `CLIENT_SECRET`. See the
   inline comments in `.env.example` for examples covering common providers.
4. **Bring it up.**
   ```bash
   docker compose up -d --build
   ```

That's it. The proxy will fetch your IdP's discovery document on startup
and start enforcing auth on every MCP call.

## Consuming from a client

Any MCP client that supports HTTP transport + OAuth works. Example client
config (Claude Code's JSON shape):

```json
{
  "mcpServers": {
    "playwright": {
      "type": "http",
      "url": "https://playwright-mcp.example.com/mcp"
    }
  }
}
```

On first connect the client walks the OAuth flow against your IdP (a
browser window opens for login). The token is cached locally — subsequent
headless runs reuse it until it expires.

## Notes

- The upstream image only supports **headless Chromium**.
- The proxy is **stateless** — no DB, no on-disk session store. Restart
  freely.
- If `OWN_SERVER_URL` changes, re-register (or update) the OAuth client in
  your IdP so the redirect URI matches.

## License

Apache 2.0 — see [LICENSE](LICENSE). Matches the upstream
[`microsoft/playwright-mcp`](https://github.com/microsoft/playwright-mcp)
license.
