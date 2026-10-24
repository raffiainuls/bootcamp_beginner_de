FROM python:3.11-slim
WORKDIR /workspace
COPY pertemuan-5/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    "dagster>=1.10,<2" "dagster-webserver>=1.10,<2"
COPY . /workspace
ENV PYTHONPATH=/workspace

