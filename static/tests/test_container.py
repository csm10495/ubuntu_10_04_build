import docker
import os
import subprocess
import sys

SIMPLE_CPP_SOURCE = '''
#include <string>
#include <iostream>

int main()
{
    std::cout << "Hello World" << std::endl;
    int a = 5;
    std::cout << "Five: " << a << " / " << std::to_string(a) << std::endl;

    return 0;
}

'''

SIMPLE_C_SOURCE = r'''
#include <string.h>
#include <stdio.h>

int main()
{
    printf("Hello World\n");
    int a = 5;
    printf("Five: %d\n", a);

    return 0;
}

'''

def test_get_container_info(bc):
    ''' used to get some info that may be useful to future debug '''
    bc.cmd('update-alternatives --get-selections')

    # no idea how to do this just with the python docker sdk
    print ("Image Size: %s" % subprocess.check_output('docker images %s --format "{{.Size}}"' % bc.image.tags[0], shell=True).decode())

def test_volume_mount(bc):
    bc.cmd('touch /mnt/cwd/test')
    os.remove(os.path.join(os.getcwd(), 'test'))

def test_has_old_glibc(bc):
    output = bc.cmd('ldd --version')
    assert 'EGLIBC 2.11.1' in output

def test_gcc_version(bc):
    output = bc.cmd('gcc --version')
    assert '8.2.0' in output

def test_gpp_version(bc):
    output = bc.cmd('g++ --version')
    assert '8.2.0' in output

def test_git_can_clone_https(bc):
    output = bc.cmd('git clone https://github.com/csm10495/ginst.git')

def test_curl_version(bc):
    output = bc.cmd('curl --version')
    assert 'unreleased' in output

def test_openssl_version(bc):
    output = bc.cmd('openssl version')
    assert '1.1.1' in output

def test_simple_cpp_exe_old_abi_32(bc):
    with open("test.cpp", 'w') as f:
        f.write(SIMPLE_CPP_SOURCE)

    # -D_GLIBCXX_USE_CXX11_ABI=0 is implicit with our specially built gcc
    bc.cmd('g++ -m32 -std=c++17 /mnt/cwd/test.cpp -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.cpp')
    os.remove('test')

def test_simple_cpp_exe_static_cpp_32(bc):
    with open("test.cpp", 'w') as f:
        f.write(SIMPLE_CPP_SOURCE)

    bc.cmd('g++ -m32 -std=c++17 -static-libstdc++ /mnt/cwd/test.cpp -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.cpp')
    os.remove('test')

def test_simple_c_exe_32(bc):
    with open("test.c", 'w') as f:
        f.write(SIMPLE_C_SOURCE)

    bc.cmd('gcc -m32 /mnt/cwd/test.c -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.c')
    os.remove('test')

def test_simple_cpp_exe_old_abi_64(bc):
    with open("test.cpp", 'w') as f:
        f.write(SIMPLE_CPP_SOURCE)

    # -D_GLIBCXX_USE_CXX11_ABI=0 is implicit with our specially built gcc
    bc.cmd('g++ -std=c++17 -m64 /mnt/cwd/test.cpp -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.cpp')
    os.remove('test')

def test_simple_cpp_exe_static_cpp_64(bc):
    with open("test.cpp", 'w') as f:
        f.write(SIMPLE_CPP_SOURCE)

    bc.cmd('g++ -std=c++17 -m64 -static-libstdc++ /mnt/cwd/test.cpp -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.cpp')
    os.remove('test')

def test_simple_c_exe_64(bc):
    with open("test.c", 'w') as f:
        f.write(SIMPLE_C_SOURCE)

    bc.cmd('gcc -m64 /mnt/cwd/test.c -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.c')
    os.remove('test')
