#!/usr/bin/env bash
export PYTHONPATH=$(pwd)/src:$(pwd)
uvicorn apps.api.app.main:app --reload
