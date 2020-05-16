FROM python:3-alpine
MAINTAINER Stamatis Katsaounis "skatsaounis@admin.grnet.gr"

ARG BRANCH=master

RUN apk --no-cache add --update ipmitool && \
    apk --no-cache add --virtual .build-deps --update \
        git \
        gcc \
        make \
        libffi-dev \
        musl-dev && \
    pip3 install --no-cache-dir git+git://github.com/grnet/maas2netbox.git@$BRANCH && \
    mkdir -p /usr/local/lib/python3.6/site-packages/maas2netbox/user_config && \
    apk del .build-deps
