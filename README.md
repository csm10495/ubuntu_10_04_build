# ubuntu_10_04_build
Dockerized Ubuntu 10.04 Build Environment [![Build Status](https://csm10495.visualstudio.com/ubuntu_10_04_build/_apis/build/status/ubuntu_10_04_build-CI)](https://csm10495.visualstudio.com/ubuntu_10_04_build/_build/latest?definitionId=2)

Sometimes we need to build things so that they work in old-legacy (unsupported/unsafe) environments. Building in this container can often allow executables to be used in most Linux builds after (and including) Ubuntu 10.04 (So 2010ish and later).

There are two versions of this: static and dynamic:

# Dynamic
Dynamic will attempt to wget and build modules within the Ubuntu 10.04 containter. This may be a bit 'yucky' from the security perspective since wget and even ssh doesn't seem to work well within the container (without newer openssl and others). So we skirt around some security in order to get the job done and build the container.

Honestly dynamic is not intended to really be used and was more of a testing platform. I'm not planning on updating dynamic anynmore.

# Static
Static is built and updated on the docker hub under: https://hub.docker.com/r/csm10495/ubuntu_10_04_build/

This repo has a few submodules, make sure to clone this recursively if building manuallly. Then run 

``` python make_dockerfile.py ```

this will update the submodule repos to release versions and generate a Dockerfile to be built in the static directory. Upon building that dockerfile, those submodule repos will be passed to the container built. This is more secure since we used (our up-to-date) git on our 'real machine' and not in the container (with an older version).

The image includes gcc-8.2.0 with multilib and C/C++ support, curl, git, and openssl all built and ready for some level of usage. Check make_dockerfile.py for the latest versions being used in the image.

To get the latest static image and run a bash shell in it try:

``` docker run -it csm10495/ubuntu_10_04_build ```

# Example
Example playing in bash inside a statically created container:

```
root@8237c9564ed6:/usr/local/dev/ginst# ldd --version
ldd (Ubuntu EGLIBC 2.11.1-0ubuntu7.21) 2.11.1
Copyright (C) 2009 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
Written by Roland McGrath and Ulrich Drepper.
root@8237c9564ed6:/usr/local/dev/ginst# /usr/local/gcc-8.2.0/bin/gcc-8.2.0 --version
gcc-8.2.0 (GCC) 8.2.0
Copyright (C) 2018 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

root@8237c9564ed6:/usr/local/dev/ginst# /usr/local/gcc-8.2.0/bin/g++-8.2.0 --version
g++-8.2.0 (GCC) 8.2.0
Copyright (C) 2018 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

root@8237c9564ed6:/usr/local/dev/ginst# /usr/local/openssl/bin/openssl version
OpenSSL 1.1.1  11 Sep 2018
root@8237c9564ed6:/usr/local/dev/ginst#

```

