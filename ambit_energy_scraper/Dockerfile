ARG BUILD_FROM=ghcr.io/hassio-addons/base:11.0.0
FROM $BUILD_FROM

LABEL io.hass.name="Ambit Energy Scraper" \
      io.hass.description="Extracts and sends Ambit Energy data to Home Assistant" \
      io.hass.version="0.1.0" \
      io.hass.type="addon"

ENV LANG C.UTF-8

# Install dependencies
RUN apk add --no-cache \
    chromium \
    chromium-chromedriver \
    python3 \
    py3-pip \
    # Add build tools if needed
    build-base

# Upgrade pip and install Python packages
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install selenium beautifulsoup4 requests

# Copy files
COPY run.sh /run.sh
RUN chmod a+x /run.sh

COPY ambit_energy_scraper.py /usr/local/bin/ambit_energy_scraper.py
RUN chmod a+x /usr/local/bin/ambit_energy_scraper.py

WORKDIR /usr/local/bin

CMD [ "/run.sh" ]

