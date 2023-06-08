FROM python:3.10

# Path: /app
WORKDIR /app
COPY . /app
RUN apt-get update -y
RUN apt-get install libpq-dev -y
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"] 