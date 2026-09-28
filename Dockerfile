FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends procps iputils-ping \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home toolkit \
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
