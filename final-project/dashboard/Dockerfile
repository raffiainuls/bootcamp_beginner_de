FROM python:3.11-slim

WORKDIR /app

COPY dashboard/requirements.txt /tmp/dashboard-requirements.txt
RUN pip install --no-cache-dir --retries 5 --timeout 60 \
    --index-url https://pypi.org/simple \
    -r /tmp/dashboard-requirements.txt

COPY dashboard /app/dashboard

EXPOSE 8000

CMD ["uvicorn", "dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]
