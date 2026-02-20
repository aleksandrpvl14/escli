FROM python:3.11-slim-alpine

WORKDIR /app

COPY escli.py .

ENTRYPOINT ["python", "escli.py"]