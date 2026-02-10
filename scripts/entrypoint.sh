#!/usr/bin/env bash
set -e

PORT="${PORT:=8000}"
fastapi dev esm_fullstack_challenge/main.py --host 0.0.0.0 --port ${PORT}
