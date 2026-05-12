FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml ./
RUN mkdir -p src/playwright_mcp_oidc && touch src/playwright_mcp_oidc/__init__.py \
 && uv sync --no-dev --no-install-project

COPY src/ src/
RUN uv sync --no-dev

CMD ["uv", "run", "--no-dev", "python", "-m", "playwright_mcp_oidc"]
