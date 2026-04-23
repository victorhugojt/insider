#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

uv run adk deploy agent_engine \
  --project=project-2c268745-0c2f-477a-b6a \
  --region=us-central1 \
  --display_name="insider_pipeline" \
  src/insider_pipeline
