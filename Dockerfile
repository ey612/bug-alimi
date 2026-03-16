FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--chdir", "src", "jira_webhook:app"]