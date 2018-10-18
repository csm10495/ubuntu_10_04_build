
import contextlib
import os
import subprocess
from six.moves.urllib.request import urlopen

DOCKERFILE_BASE = \
'''
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

# OpenSSL
ADD openssl /usr/local/dev/openssl
RUN fromdos /usr/local/dev/openssl/*
RUN fromdos /usr/local/dev/openssl/*/**
WORKDIR /usr/local/dev/openssl
RUN chmod +x config
RUN ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib
RUN make -j4
RUN make install
RUN echo "/usr/local/openssl/lib" >> /etc/ld.so.conf.d/openssl.conf
RUN ldconfig -v
RUN /usr/local/openssl/bin/openssl version

# Curl
ADD curl /usr/local/dev/curl
WORKDIR /usr/local/dev/curl
RUN chmod +x buildconf
RUN ./buildconf
#  --disable-shared
RUN LIBS="-ldl" ./configure --with-ssl=/usr/local/openssl --prefix=/usr/local/curl
RUN make -j4
RUN make install
RUN /usr/local/curl/bin/curl --version

# Add cacert.pem
WORKDIR /usr/local/
ADD cacert.pem cacert.pem

# Git
ADD git /usr/local/dev/git
WORKDIR /usr/local/dev/git
RUN fromdos *
RUN fromdos */**
RUN make configure
RUN ./configure --with-openssl=/usr/local/openssl --prefix=/usr/local/git --with-curl=/usr/local/curl
RUN make -j4
RUN chmod +x check_bindir
RUN make install
RUN /usr/local/git/bin/git --version
RUN echo "Host github.com\\n\\tStrictHostKeyChecking no\\n" >> /etc/ssh/ssh_config

# Tell git to use the new certs
RUN echo "[http]" >> ~/.gitconfig
RUN echo "sslCAinfo = /usr/local/cacert.pem" >> ~/.gitconfig

# GCC
WORKDIR /usr/local/dev
ADD gcc /usr/local/dev/gcc
ADD ginst /usr/local/dev/ginst
WORKDIR /usr/local/dev/ginst
RUN python -c "from ginst import *; g = GInst('8.2.0');g.installFromFolder('/usr/local/dev/gcc')"

# Aliases for bash
RUN echo "alias g++=/usr/local/gcc-8.2.0/bin/g++-8.2.0" >> ~/.bashrc
RUN echo "alias gcc=/usr/local/gcc-8.2.0/bin/gcc-8.2.0" >> ~/.bashrc
RUN echo "alias curl=/usr/local/curl/bin/curl" >> ~/.bashrc
RUN echo "alias git=/usr/local/git/bin/git" >> ~/.bashrc
RUN echo "alias openssl=/usr/local/openssl/bin/openssl" >> ~/.bashrc

CMD "/bin/bash"
'''

GIT_CHECKOUTS = {
    'curl' : '432eb5f5c254ee8383b2522ce597c9219877923e', # 7.61.1 release
    'gcc'  : '9fb89fa845c1b2e0a18d85ada0b077c84508ab78', # 8.2.0
    'ginst'  : 'master', # tip
    'git'  : 'cae598d9980661a978e2df4fb338518f7bf09572', # 2.19.1 release
    'openssl' : '1708e3e85b4a86bae26860aa5d2913fc8eff6086', # 1.1.1 release
}

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))

@contextlib.contextmanager
def tmpChdir(d):
    cur = os.getcwd()
    os.chdir(d)
    try:
        yield
    finally:
        os.chdir(cur)

def downloadCertificateStore():
    with open(os.path.join(THIS_FOLDER, 'cacert.pem'), 'wb') as f:
        f.write(urlopen('https://curl.haxx.se/ca/cacert.pem').read())

def getAllReposToDesiredCheckouts(clean=True):
    for repo, changeset in GIT_CHECKOUTS.items():
        with tmpChdir(os.path.join(THIS_FOLDER, repo)):
            if subprocess.call('git checkout %s' % changeset, shell=True) != 0:
                raise EnvironmentError("Failed to checkout repo %s -> %s" % (repo, changeset))
            if clean:
                # Hopefully this will make it so we don't need a rebuild even if we messed with stuff a bit
                print ("Cleaning: %s" % repo)
                if subprocess.call('git clean -df', shell=True) != 0:
                    raise EnvironmentError("Failed to clean repo %s" % repo)

def writeDockerfile():
    with open(os.path.join(THIS_FOLDER, 'Dockerfile'), 'w') as f:
        f.write(DOCKERFILE_BASE)

if __name__ == '__main__':
    print ('Getting Repos to Desired Changesets')
    getAllReposToDesiredCheckouts()
    print ('Downloading latest Certificate Store')
    downloadCertificateStore()
    print ('Writing Dockerfile!')
    writeDockerfile()
    print ('Done!')