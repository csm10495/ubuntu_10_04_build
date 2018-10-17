FROM ubuntu:10.04

# This Ubuntu doesn't have its packages on the normal server anymore
RUN sed -i -e "s/archive.ubuntu.com/old-releases.ubuntu.com/g" /etc/apt/sources.list

# Get some starter things
RUN apt-get update
RUN apt-get install tar wget gcc g++ make nano libc6-dev-i386 python-pip python-dev -y
RUN apt-get install python-argparse build-essential ia32-libs gcc-multilib g++-multilib -y
RUN apt-get install git-core python libcurl4-openssl-dev libz-dev gettext zlib1g-dev -y
RUN apt-get install checkinstall libgnutls-dev curl autoconf libtool -y

# Build new OpenSSL (needed for newer git and https to work)
WORKDIR /usr/local
RUN wget https://www.openssl.org/source/openssl-1.0.2o.tar.gz
RUN wget https://www.openssl.org/source/openssl-1.0.2o.tar.gz.sha1 -O openssl.sha1
RUN sha1sum openssl-1.0.2o.tar.gz > openssl.tar.gz.calc.sha1
# verify SHA1
RUN python -c "assert open('openssl.sha1').read().strip() in open('openssl.tar.gz.calc.sha1').read().strip()"
# Continue with OpenSSL
RUN tar -xvzf openssl-1.0.2o.tar.gz
WORKDIR /usr/local/openssl-1.0.2o
RUN ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib
RUN make -j4
RUN make install
RUN echo "/usr/local/openssl/lib" >> /etc/ld.so.conf.d/openssl-1.0.2o.conf
RUN ldconfig -v
RUN /usr/local/openssl/bin/openssl version
# TODO CLEANUP

# Build new Git
WORKDIR /usr/local
RUN wget https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.9.5.tar.gz
RUN tar -xvzf git-2.9.5.tar.gz
WORKDIR /usr/local/git-2.9.5
RUN ./configure --with-openssl=/usr/local/openssl
RUN make -j4
RUN make install
RUN git --version
RUN echo "Host github.com\n\tStrictHostKeyChecking no\n" >> /etc/ssh/ssh_config
# TODO CLEANUP

# Build new curl with new OpenSSL for Git
WORKDIR /usr/local
# Is the commit id below safe enough to say SSL_NO_VERIFY is ok?
RUN GIT_SSL_NO_VERIFY=true git clone https://github.com/curl/curl.git
WORKDIR /usr/local/curl
RUN git checkout 432eb5f5c254ee8383b2522ce597c9219877923e
RUN ./buildconf
RUN LIBS="-ldl" ./configure --with-ssl=/usr/local/openssl --disable-shared
RUN make -j4
RUN make install
RUN curl --version
# TODO CLEANUP

# Download the latest .pem file for https connections via curl
RUN /usr/local/curl/src/curl https://curl.haxx.se/ca/cacert.pem -o /cacert.pem
# Tell git to use the new certs
RUN echo "[http]" >> ~/.gitconfig
RUN echo "sslCAinfo = /cacert.pem" >> ~/.gitconfig

# Build GCC-8.2
WORKDIR /usr/local
RUN git clone https://github.com/csm10495/ginst.git
WORKDIR /usr/local/ginst
RUN git checkout 20e10834c3beed90bf90a6c2ae2a6d89d2754f0f
RUN python -c "from ginst import *; g = GInst('8.2.0');g.install()"
# TODO CLEANUP

# Force our terminal to use this GCC 8.2 instead of the default
RUN echo "alias g++=/usr/local/gcc-8.2.0/bin/g++-8.2.0" >> ~/.bashrc
RUN echo "alias gcc=/usr/local/gcc-8.2.0/bin/gcc-8.2.0" >> ~/.bashrc

# Let's go!
WORKDIR /
CMD "/bin/bash"

#16M     /usr/local/bin
#4.0K    /usr/local/etc
#4.0K    /usr/local/games
#956M    /usr/local/gcc-8.2.0
#7.5G    /usr/local/ginst
#242M    /usr/local/git-2.9.5
#5.7M    /usr/local/git-2.9.5.tar.gz
#4.0K    /usr/local/include
#40K     /usr/local/lib
#46M     /usr/local/libexec
#0       /usr/local/man
#15M     /usr/local/openssl
#49M     /usr/local/openssl-1.0.2o
#5.1M    /usr/local/openssl-1.0.2o.tar.gz
#4.0K    /usr/local/openssl.sha1
#4.0K    /usr/local/openssl.tar.gz.calc.sha1
#4.0K    /usr/local/sbin
#5.6M    /usr/local/share
#4.0K    /usr/local/src
