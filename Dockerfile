FROM ghcr.io/astral-sh/uv:python3.12-bookworm
WORKDIR /workspace
COPY . .
RUN uv sync --all-packages
CMD ["uv", "run", "pytest", "-q"]
