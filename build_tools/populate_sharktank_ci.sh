#!/bin/bash

IMPORTER=1 BENCHMARK=1 ./setup_venv.sh
source $GITHUB_WORKSPACE/shark.venv/bin/activate
python generate_sharktank.py --upload=False --ci_tank_dir=True
