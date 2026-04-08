# =============================================================
# Fixi Agent — Multi-stage Dockerfile
# =============================================================
# Produces a container with Python 3.12 + Node 22 + Claude Code
# CLI + the fixi-agent package installed.
#
# Usage:
#   docker build -t fixi-agent .
#   docker run -e ANTHROPIC_API_KEY=... fixi-agent resolve \
#     --work-item <url> --repo <url>
#
# Size target: < 1.5 GB
# =============================================================

# --- Stage 1: Node + Claude Code CLI ---
FROM node:22-slim AS node-stage

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code \
    && claude --version \
    && npm cache clean --force

# --- Stage 2: Build the Python wheel ---
FROM python:3.12-slim-bookworm AS python-build

WORKDIR /build
COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir build \
    && python -m build --wheel --outdir /build/dist

# --- Stage 3: Final runtime image ---
FROM python:3.12-slim-bookworm

LABEL maintainer="Lots of Context LLC"
LABEL description="Fixi — Autonomous issue resolution agent"
LABEL org.opencontainers.image.source="https://github.com/lotsofcontext/fixi"

# Install git (required for clone, branch, push operations)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Node.js runtime + Claude Code CLI from node-stage
COPY --from=node-stage /usr/local/bin/node /usr/local/bin/node
COPY --from=node-stage /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/.bin/claude /usr/local/bin/claude \
    && claude --version

# Copy and install the Python wheel
COPY --from=python-build /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl \
    && rm /tmp/*.whl \
    && fixi --version

# Copy the skill/ directory (system prompt + references)
# This is loaded at runtime by prompts.py
COPY --from=python-build /build/src /opt/fixi/src
WORKDIR /opt/fixi

# The skill/ dir is expected at the repo root level.
# In production, mount it or copy it into the image:
#   COPY skill/ /opt/fixi/skill/
# For now, the user must pass --skill-dir or mount a volume.

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash fixi
USER fixi

# Default working directory for cloned repos
WORKDIR /workspace

# Environment variables (override at runtime)
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Entry point
ENTRYPOINT ["fixi"]
CMD ["--help"]

# =============================================================
# Examples:
#
#   # Build
#   docker build -t fixi-agent -f agent/Dockerfile agent/
#
#   # Run with skill/ mounted from host
#   docker run --rm \
#     -e ANTHROPIC_API_KEY=sk-ant-... \
#     -e GH_TOKEN=ghp_... \
#     -v /path/to/fixi/skill:/opt/fixi/skill:ro \
#     fixi-agent resolve \
#       --work-item https://github.com/org/repo/issues/42 \
#       --repo https://github.com/org/repo \
#       --skill-dir /opt/fixi/skill \
#       --output json
#
#   # Or with docker-compose (see docker-compose.yml)
# =============================================================
