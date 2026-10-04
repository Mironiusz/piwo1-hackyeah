FROM postgres:18.6-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-18-postgis-3=3.6.4+dfsg-2.pgdg13+1 \
        postgresql-18-pgrouting=4.0.1-1.pgdg13+1 \
    && rm -rf /var/lib/apt/lists/*

COPY create_accounts.sh /docker-entrypoint-initdb.d/10_create_accounts.sh
