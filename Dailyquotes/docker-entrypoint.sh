#!/bin/sh

echo "Registering cron job..."
crontab /app/crontab

echo "Starting cron..."
cron -f
