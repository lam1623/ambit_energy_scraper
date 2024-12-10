ARG BUILD_FROM
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Copy root filesystem
COPY rootfs /

# Install required packages
# selenium, chromium, chromedriver, python libraries
RUN apk add --no-cache \
    chromium \
    chromium-chromedriver \
    bash \
    jq \
    curl \
    coreutils \
    tzdata \
    && pip3 install selenium beautifulsoup4 requests

# Make run.sh executable
RUN chmod +x /usr/src/app/run.sh

# Labels
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Home Assistant Community Add-ons" \
    org.opencontainers.image.authors="Your Name <you@example.com>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/your-repo/ambit_energy_scraper" \
    org.opencontainers.image.source="https://github.com/your-repo/ambit_energy_scraper" \
    org.opencontainers.image.documentation="https://github.com/your-repo/ambit_energy_scraper/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}

# Default command
CMD [ "/usr/src/app/run.sh" ]

