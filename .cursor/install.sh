#!/usr/bin/env bash
set -euo pipefail

# Install core Agno runtime dependencies.
python3 -m pip install -r requirements-agno.txt

# Optional provider dependencies.
python3 -m pip install -r requirements-agno-providers-optional.txt

# Smoke-check that the default validation command is executable.
python3 -m agno_runtime --registry-root agno_registry validate
