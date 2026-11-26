# Build context: examples/livre-dor
FROM python:3.12-slim
WORKDIR /srv/bot
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot/bot.py bot/livredor.py ./
RUN useradd --system --uid 10001 app
USER 10001
CMD ["python", "bot.py"]
