#!/usr/bin/with-contenv bashio

# Extraer valores de configuración
USERNAME=$(bashio::config 'username')
PASSWORD=$(bashio::config 'password')
HA_URL=$(bashio::config 'ha_url')
HA_TOKEN=$(bashio::config 'ha_token')

bashio::log.info "Iniciando Ambit Energy Scraper..."
bashio::log.info "Enviando datos a Home Assistant en $HA_URL"

# Ejecutar el script de Python con las configuraciones
python3 /app/ambit_energy_scraper.py --username "$USERNAME" --password "$PASSWORD" --ha-url "$HA_URL" --ha-token "$HA_TOKEN"

