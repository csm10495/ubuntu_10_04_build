import docker
import pytest
import os

def __exec(bc, cmd, expectedRetCode=0):
    print ('\n<CALLING>: %s' % cmd)
    retCode, output = bc.exec_run(cmd)
    output = output.decode()
    print('\n<CONTAINER>: ' + '\n<CONTAINER>: '.join(output.splitlines()))
    assert retCode == expectedRetCode
    return output

@pytest.fixture(scope="function")
def buildContainer():
    client = docker.from_env()
    volumes = {
        os.getcwd() : {
            'bind' : '/mnt/cwd',
            'mode' : 'rw',
        }
    }
    container = client.containers.run('csm10495/ubuntu_10_04_build:latest', 'bash', detach=True, tty=True, volumes=volumes)
    container.cmd = lambda cmd, expectedRetCode=0 : __exec(container, cmd, expectedRetCode)
    try:
        yield container
    finally:
        container.remove(force=True)

bc = buildContainer
