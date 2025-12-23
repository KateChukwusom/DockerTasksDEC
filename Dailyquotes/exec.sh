#!/bin/bash

cd /app || exit 1

python3 scripts/init_db.py
python3 scripts/quotefetcher.py
python3 scripts/emailsender.py
python3 scripts/adminsummary.py

echo "$(date): Daily run completed" >> logs/exec.log
