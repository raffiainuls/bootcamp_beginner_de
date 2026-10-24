FROM prefecthq/prefect:3-python3.11
WORKDIR /workspace
COPY pertemuan-5/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY . /workspace
ENV PYTHONPATH=/workspace

