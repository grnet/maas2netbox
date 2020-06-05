FROM python:3-alpine
MAINTAINER Stamatis Katsaounis "skatsaounis@admin.grnet.gr"

ARG BRANCH=master

RUN apk --no-cache add --virtual .build-deps --update \
        git \
        gcc \
        make \
        libffi-dev \
        musl-dev && \
    pip3 install --no-cache-dir git+git://github.com/grnet/maas2netbox.git@$BRANCH && \
    apk del .build-deps
