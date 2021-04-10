FROM python:3.9-slim-buster

COPY . /app/api
WORKDIR /app/api

RUN apt-get update && apt-get install libpq-dev gcc -y \
    && python3 -m pip install -r requirements.txt \
    && apt-get remove gcc -y && apt-get autoremove -y \
    && apt-get clean

EXPOSE 5000

ENTRYPOINT [ "python3", "app.py" ]
# ENTRYPOINT [ "flask", "run", "--host=0.0.0.0" ]