FROM python:3.13-alpine

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000
EXPOSE 9001
EXPOSE 9002

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]

LABEL org.opencontainers.image.source=https://github.com/X104n/data-mesh