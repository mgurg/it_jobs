#!/usr/bin/bash
cd "${0%/*}"
source .venv/bin/activate
echo "Activated"
python app.py
echo "Done"

