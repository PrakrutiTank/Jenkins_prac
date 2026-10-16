FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir flask requests scikit-learn numpy pytest

COPY model.pkl .
COPY templates/ templates/
COPY test_sample.py .
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
