#!/usr/bin/env bash
python bot.py &
cd website && gunicorn app:app --bind 0.0.0.0:$PORT
