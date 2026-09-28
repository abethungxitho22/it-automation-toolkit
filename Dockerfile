# Keep the runtime small: this toolkit only needs Python's standard library.
FROM python:3.12-alpine3.24

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk upgrade --no-cache \
    && apk add --no-cache procps iputils \
    && addgroup -g 10001 toolkit \
    && adduser -D -u 10001 -G toolkit toolkit \
    && mkdir /data \
    && chown toolkit:toolkit /data

WORKDIR /app
COPY main.py file_organiser.py log_analyser.py health_checker.py ./
COPY data_validator.py report_generator.py system_setup.py setup_config.json ./
COPY sample.log records.csv expected_files.txt ./
COPY test_data/ ./test_data/

USER 10001:10001
WORKDIR /data
ENTRYPOINT ["python", "/app/main.py"]
CMD ["--help"]
