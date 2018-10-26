import docker
import os

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

def test_simple_cpp_exe_old_abi(bc):
    with open("test.cpp", 'w') as f:
        f.write(SIMPLE_CPP_SOURCE)

    bc.cmd('g++ -std=c++17 -D_GLIBCXX_USE_CXX11_ABI=0 /mnt/cwd/test.cpp -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.cpp')
    os.remove('test')

def test_simple_cpp_exe_static_cpp(bc):
    with open("test.cpp", 'w') as f:
        f.write(SIMPLE_CPP_SOURCE)

    bc.cmd('g++ -std=c++17 -static-libstdc++ /mnt/cwd/test.cpp -o /mnt/cwd/test')
    bc.cmd('chmod +x /mnt/cwd/test')
    bc.cmd('/mnt/cwd/test')

    assert os.system('./test') == 0

    os.remove('test.cpp')
    os.remove('test')
