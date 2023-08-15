FROM python:3.11

WORKDIR /app

RUN apt update -y
RUN apt-get install -y wget git

COPY requirements.txt requirements.txt
RUN pip3 install -U -r requirements.txt

COPY start.sh start.sh

CMD ["bash","start.sh"]