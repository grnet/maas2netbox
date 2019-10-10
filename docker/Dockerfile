FROM centos:7
MAINTAINER Stamatis Katsaounis "skatsaounis@admin.grnet.gr"

ARG BRANCH=master

RUN yum install -y \
        wget \
        unzip \
        ipmitool \
        python3 \
        git && \
    wget https://download.lenovo.com/pccbbs/thinkservers/osput_1.3.2.zip && \
    unzip osput_1.3.2.zip && \
    yum install -y OSPUT-1.3.2/osput-1.3.2-1-rhel.x86_64.rpm && \
    rm -rf osput_1.3.2.zip OSPUT-1.3.2 && \
    yum clean all

RUN git init /src/maas2netbox && \
    (cd /src/maas2netbox && \
        git fetch --tags https://github.com/grnet/maas2netbox.git $BRANCH && \
        git checkout FETCH_HEAD) && \
    pip3 install --no-cache-dir /src/maas2netbox && \
    rm -r /src/maas2netbox && \
    mkdir -p /usr/local/lib/python3.6/site-packages/maas2netbox/user_config
