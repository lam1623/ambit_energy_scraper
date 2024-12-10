ARG BUILD_FROM
FROM $BUILD_FROM

# Instalar dependencias necesarias
RUN apk add --no-cache \
      python3 \
      py3-pip \
      chromium \
      chromium-chromedriver

# Instalar paquetes Python requeridos
RUN pip3 install selenium beautifulsoup4 requests

# Copiar el script al sistema de archivos del contenedor
COPY run.sh /
COPY ambit_energy_scraper.py /app/ambit_energy_scraper.py
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

