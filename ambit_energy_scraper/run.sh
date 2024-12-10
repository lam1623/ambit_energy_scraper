#!/usr/bin/env bash
set -e

# Read options from /data/options.json if needed
# For example, reading HA_TOKEN from config:
HA_TOKEN=$(jq --raw-output '.ha_token' /data/options.json)
HA_URL=$(jq --raw-output '.ha_url' /data/options.json)
USERNAME=$(jq --raw-output '.username' /data/options.json)
PASSWORD=$(jq --raw-output '.password' /data/options.json)

export HA_TOKEN=${HA_TOKEN}
export HA_URL=${HA_URL}
export USERNAME=${USERNAME}
export PASSWORD=${PASSWORD}

echo "Starting Ambit Energy Scraper add-on..."

# Run the script periodically or once.
# If you prefer periodic execution, you can implement a loop with sleep.
# For example, run every 6 hours:
while true; do
    python3 /usr/local/bin/ambit_energy_scraper.py
    echo "Script run complete, sleeping for 6 hours..."
    sleep 6h
done

