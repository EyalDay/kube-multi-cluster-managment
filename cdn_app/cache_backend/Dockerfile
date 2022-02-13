FROM python:3.9

RUN mkdir -p /app

COPY /cache_backend/__init__.py /app
COPY /cache_backend/cache_backend.py /app
COPY /cache_backend//fake_connection.py /app
COPY /cache_backend/utils.py /app
COPY /requirements.txt/ /app
RUN pip3 install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
# For local testing
EXPOSE 8081
CMD ["python", "cache_backend.py"]
