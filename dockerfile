FROM apache/airflow:3.1.0

USER root
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   gcc \
	   libpq-dev \
	   python3-dev \
	&& rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt