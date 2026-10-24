FROM python:3.11-slim

WORKDIR /workspace/final-project

COPY orchestration/requirements.txt /tmp/final-project-requirements.txt
RUN pip install --no-cache-dir --retries 5 --timeout 60 \
    --index-url https://pypi.org/simple \
    -r /tmp/final-project-requirements.txt

COPY . /workspace/final-project

ENV PYTHONPATH=/workspace/final-project
ENV DAGSTER_HOME=/opt/dagster/dagster_home

RUN mkdir -p /opt/dagster/dagster_home
