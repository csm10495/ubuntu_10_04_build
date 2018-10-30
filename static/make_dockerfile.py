
import contextlib
import os
import subprocess
from six.moves.urllib.request import urlopen

DOCKERFILE_BASE = \
'''
FROM ubuntu:10.04

# This Ubuntu doesn't have its packages on the normal server anymore also get some starter things
RUN sed -i -e "s/archive.ubuntu.com/old-releases.ubuntu.com/g" /etc/apt/sources.list && \
    apt-get update && apt-get install tar wget gcc g++ make nano libc6-dev-i386 python-pip python-dev python-argparse \
    build-essential gcc-multilib g++-multilib python libcurl4-openssl-dev libz-dev gettext zlib1g-dev \
    checkinstall libgnutls-dev autoconf libtool tofrodos automake -y --no-install-recommends && \
    apt-get clean && apt-get autoclean && apt-get autoremove -y  && \
    mkdir -p /usr/local/dev/

WORKDIR /usr/local/dev/

# OpenSSL
ADD openssl /usr/local/dev/openssl
WORKDIR /usr/local/dev/openssl
RUN fromdos /usr/local/dev/openssl/* && fromdos /usr/local/dev/openssl/*/** && chmod +x config && \
    ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib && make -j4 && make install && \
    echo "/usr/local/openssl/lib" >> /etc/ld.so.conf.d/openssl.conf && ldconfig -v && /usr/local/openssl/bin/openssl version

# Curl
ADD curl /usr/local/dev/curl
WORKDIR /usr/local/dev/curl
RUN chmod +x buildconf && ./buildconf && LIBS="-ldl" ./configure --with-ssl=/usr/local/openssl --prefix=/usr/local/curl && make -j4 && \
    make install && /usr/local/curl/bin/curl --version

# Add cacert.pem
WORKDIR /usr/local/
ADD cacert.pem cacert.pem

# Git (and telling it to use new certs)
ADD git /usr/local/dev/git
WORKDIR /usr/local/dev/git
RUN fromdos * && fromdos */** && mkdir -p /etc/ssh && make configure && ./configure --with-openssl=/usr/local/openssl --prefix=/usr/local/git --with-curl=/usr/local/curl && \
    make -j4 && chmod +x check_bindir && make install && /usr/local/git/bin/git --version && \
    echo "Host github.com\\n\\tStrictHostKeyChecking no\\n" >> /etc/ssh/ssh_config && \
    echo "[http]" >> ~/.gitconfig && \
    echo "sslCAinfo = /usr/local/cacert.pem" >> ~/.gitconfig

# GCC
WORKDIR /usr/local/dev
ADD gcc /usr/local/dev/gcc
ADD ginst /usr/local/dev/ginst
WORKDIR /usr/local/dev/ginst
RUN python -c "from ginst import *; gccVersion = GccVersion('8.2.0', '--with-default-libstdcxx-abi=gcc4-compatible');g = GInst(gccVersion);g.installFromFolder('/usr/local/dev/gcc')" && \
    apt-get clean && apt-get autoclean && apt-get autoremove -y

# Update alternatives
RUN update-alternatives --install /usr/bin/g++ g++ /usr/local/gcc-8.2.0/bin/g++-8.2.0 50 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/local/gcc-8.2.0/bin/gcc-8.2.0 50 && \
    update-alternatives --install /usr/bin/curl curl /usr/local/curl/bin/curl 50 && \
    update-alternatives --install /usr/bin/git git /usr/local/git/bin/git 50 && \
    update-alternatives --install /usr/bin/openssl openssl /usr/local/openssl/bin/openssl 50 && \
    yes '' | update-alternatives --force --all

# Delete un-needed sources (and packages) (and save space)
RUN rm -rf /usr/local/dev && \
    rm /var/lib/apt/lists/*ubuntu*

WORKDIR /

CMD "/bin/bash"
'''

GIT_CHECKOUTS = {
    'curl' : '432eb5f5c254ee8383b2522ce597c9219877923e', # 7.61.1 release
    'gcc'  : '9fb89fa845c1b2e0a18d85ada0b077c84508ab78', # 8.2.0
    'ginst'  : 'fe08326787a051abcd5245260d4321187c5ec7f3', # Last Good
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
            print ('Checking out: %s' % repo)
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
