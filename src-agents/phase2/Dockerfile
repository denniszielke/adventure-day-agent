FROM python:3.11

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-${WEBSITES_PORT:-8080}}"]