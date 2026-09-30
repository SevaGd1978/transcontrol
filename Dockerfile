FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# mega.py требует tenacity<6, но старый tenacity не работает на Python 3.11+.
# На практике mega.py 1.0.8 полностью совместим с современным tenacity,
# поэтому ставим mega.py без зависимостей и нужные пакеты отдельно.
RUN pip install --no-cache-dir --no-deps mega.py==1.0.8 \
    && pip install --no-cache-dir "tenacity>=8" pycryptodome requests "pathlib==1.0.1"

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
