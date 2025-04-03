FROM python:3.11-slim

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000
EXPOSE 9001

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]