
FROM ubuntu:10.04

# This Ubuntu doesn't have its packages on the normal server anymore
RUN sed -i -e "s/archive.ubuntu.com/old-releases.ubuntu.com/g" /etc/apt/sources.list

# Get some starter things
RUN apt-get update
RUN apt-get install tar wget gcc g++ make nano libc6-dev-i386 python-pip python-dev -y
RUN apt-get install python-argparse build-essential ia32-libs gcc-multilib g++-multilib -y
RUN apt-get install git-core python libcurl4-openssl-dev libz-dev gettext zlib1g-dev -y
RUN apt-get install checkinstall libgnutls-dev curl autoconf libtool tofrodos -y

RUN mkdir -p /usr/local/dev/
WORKDIR /usr/local/dev/

ADD openssl /usr/local/dev/openssl
RUN fromdos /usr/local/dev/openssl/*
RUN fromdos /usr/local/dev/openssl/*/**
WORKDIR /usr/local/dev/openssl
RUN chmod +x config
RUN ./config
RUN make -j4
RUN make install

CMD "/bin/bash"
