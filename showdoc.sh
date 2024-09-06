#!/bin/sh
python -m http.server --directory ./docs/_build/html 8000 --bind 127.0.0.1 &
python -m webbrowser http://127.0.0.1:8000
