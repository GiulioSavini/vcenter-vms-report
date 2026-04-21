FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY main.py .

VOLUME ["/app/data"]

ENTRYPOINT ["python", "main.py"]
CMD ["--list", "/app/data/vcenters_list.txt", "--format", "csv", "--output", "/app/data/vm_report.csv"]
