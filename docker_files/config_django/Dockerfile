FROM python:3.14-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos dependencias de sistema
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    # Dependencias esenciales para GeoDjango (GDAL, GEOS, PROJ)
    gdal-dev \
    geos-dev \
    proj-dev \
    proj-util \
    # Otras dependencias de compilación y utilidades
    musl-dev \
    libffi-dev \
    pango-dev \
    zlib-dev \
    jpeg-dev \
    freetype-dev \
    # Para que el shell de entrypoint funcione correctamente
    bash

# Variables de entorno para que Django encuentre las librerías GIS en Alpine
# Estas rutas son las estándar en Alpine Linux
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY initdb.sh /usr/local/bin/initdb.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/initdb.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
