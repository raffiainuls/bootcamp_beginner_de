FROM python:3.11-slim
WORKDIR /workspace
COPY pertemuan-5/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY . /workspace
ENV PGHOST=host.docker.internal PGPORT=5433 PGDATABASE=nusacode_db PGUSER=postgresdev PGPASSWORD=adminpass123 \
    CH_HOST=host.docker.internal CH_PORT=8123 CH_USER=clickhousedev CH_PASSWORD=adminpass123
CMD ["bash"]

