#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python etl.py history
python etl.py daily