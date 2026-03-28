#!/usr/bin/env bash
export PYTHONPATH=$(pwd)/src:$(pwd)
python -m apps.workers.run
