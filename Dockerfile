FROM python:3.8.6-alpine3.12
MAINTAINER david.leonard@flexential.com

RUN apk update && apk add --virtual .build-deps curl git gcc musl-dev libffi-dev libxml2-dev libxslt-dev
RUN apk add libressl-dev py3-lxml py3-cryptography

RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python3 get-pip.py
RUN pip3 --version

RUN pip3 install --upgrade pip setuptools
RUN pip3 install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git
RUN pip3 install --upgrade click

RUN apk del .build-deps

WORKDIR /opt

COPY vmconnection.py /opt/vmconnection.py
COPY main.py /opt/main.py

ENV USERNAME "username"
ENV HOSTNAME "10.0.0.1"
ENV PASSWORD "password"
ENV OUTPUT "output.json"
ENV FILTER "{}"


CMD python3 /opt/main.py --hostname $HOSTNAME --username $USERNAME --password $PASSWORD --output $OUTPUT --loop --notls --filter "$FILTER"