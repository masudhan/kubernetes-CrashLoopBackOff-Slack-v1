# Builder
FROM python:3.7-slim-buster AS builder

LABEL Maintainer="Madhu Sudhan"

# Add a work directory
WORKDIR /app

# Cache and Install dependencies
COPY requirements.txt ./

RUN pip3.7 install --no-cache-dir -r requirements.txt

# Application
FROM python:3.7-slim-buster

WORKDIR /app

COPY --from=builder /app /app/

COPY crashloop.py .

CMD [ "python3", "crashloop.py" ]

