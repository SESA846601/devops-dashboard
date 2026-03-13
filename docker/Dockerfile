FROM python:3.9-slim

WORKDIR /app

COPY app/ /app/

COPY version.txt /app/version.txt

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
