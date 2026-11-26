# Build context: examples/livre-dor (schema.sql lives beside api/)
FROM python:3.12-slim
WORKDIR /srv/api
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/app.py api/store.py api/limits.py ./
COPY schema.sql /srv/schema.sql
RUN useradd --system --uid 10001 app
USER 10001
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
