#!/usr/bin/env bash
python bot.py > bot.log 2>&1 &
cd website && gunicorn app:app --bind 0.0.0.0:$PORT
