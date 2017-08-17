FROM python:3

RUN mkdir /app
WORKDIR /app

EXPOSE 2323

CMD ["python3", "-u", "proxy.py" "2323"]

ADD proxy.py /app


