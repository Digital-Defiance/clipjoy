#!/bin/bash
# Use the virtual environment's python directly
dirname "\$0" | cd
source venv/bin/activate
python3 run.py
