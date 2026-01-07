FROM python:3.9-slim

WORKDIR /app

# set python path so imports work correctly
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "src/channels/streamlit/server.py", "--server.port=8501", "--server.address=0.0.0.0"]

