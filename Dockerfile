FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    patchright install --with-deps chromium

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "UI/job_listings.py"]
