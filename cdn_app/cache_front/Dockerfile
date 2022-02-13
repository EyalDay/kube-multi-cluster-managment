FROM python:3.9

RUN mkdir -p /app

COPY /cache_front/__init__.py /app
COPY /cache_front/cache_frontend.py /app
COPY /cache_front/fake_connection.py /app
COPY /cache_backend/utils.py /app
COPY /requirements.txt/ /app
RUN pip3 install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
# For local testing
EXPOSE 8082
CMD ["python", "cache_frontend.py"]
