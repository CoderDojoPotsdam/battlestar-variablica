FROM python:3

ENV USER=root
ENV HOME=/root

RUN wget -O- https://get.docker.com | bash

RUN mkdir /app
WORKDIR /app

EXPOSE 2323

CMD ["python3", "-u", "proxy.py" "2323"]

ADD proxy.py /app


