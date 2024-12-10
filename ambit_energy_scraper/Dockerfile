ARG BUILD_FROM
FROM $BUILD_FROM

# Instalar dependencias del sistema
RUN apk add --no-cache python3 chromium chromium-driver bash

# Instalar dependencias de Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Crear el directorio de trabajo
WORKDIR /app

# Copiar los archivos del add-on
COPY ambit_energy_scraper.py /app/
COPY run.sh /app/
COPY logo.png /app/

# Dar permisos de ejecución al script
RUN chmod +x /app/run.sh

# Definir el comando por defecto
CMD [ "/app/run.sh" ]

