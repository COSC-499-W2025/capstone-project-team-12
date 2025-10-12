FROM postgres:18.0
COPY *.sql /docker-entrypoint-initdb.d/