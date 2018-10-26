import docker
import os

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
