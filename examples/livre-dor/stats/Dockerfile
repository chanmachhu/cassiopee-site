# Build context: examples/livre-dor (schema.sql lives beside stats/)
FROM python:3.12-slim
WORKDIR /srv/stats
COPY stats/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY stats/stats.py ./
COPY schema.sql /srv/schema.sql
RUN useradd --system --uid 10001 app
USER 10001
CMD ["python", "stats.py"]
