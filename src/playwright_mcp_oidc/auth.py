"""OIDC proxy with an additional static-bearer "machine key" auth path.

Adds a single override on top of `OIDCProxy`: when a request's bearer token
matches the configured machine key (constant-time compare), short-circuit
the upstream IdP and synthesize an `AccessToken`. All other tokens fall
through to the normal OIDC verification path, so interactive OAuth keeps
working unchanged.

Leave `machine_api_key` unset (None/empty) to disable the bypass entirely.
"""

from __future__ import annotations

import hmac

from fastmcp.server.auth.auth import AccessToken
from fastmcp.server.auth.oidc_proxy import OIDCProxy


class MachineKeyOIDCProxy(OIDCProxy):
    """OIDCProxy that also accepts a single static bearer token."""

    def __init__(self, *args, machine_api_key: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Normalize "" -> None so callers don't need to filter env-string emptiness.
        self._machine_api_key = machine_api_key or None

    async def load_access_token(self, token: str) -> AccessToken | None:
        if self._machine_api_key and hmac.compare_digest(
            token, self._machine_api_key
        ):
            # expires_at=None: the key has no clock-based expiry. Rotation is
            # operational (edit env, restart). See README "Authentication modes".
            return AccessToken(
                token=token,
                client_id="machine",
                scopes=list(self.required_scopes or []),
                expires_at=None,
                claims={"sub": "machine-client", "kind": "machine"},
            )
        return await super().load_access_token(token)
