
FROM python:3.8
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "interaction_service:app", "--host", "0.0.0.0", "--port", "8002"]
