FROM python:3.9-buster

COPY src app/src
COPY requierments.txt app/requierments.txt
WORKDIR /app

RUN pip3 install -r requierments.txt && mkdir -p data/pp19-data

ENTRYPOINT [ "python3", "src/fillDB.py" ]
# ENTRYPOINT [ "/bin/bash" ]