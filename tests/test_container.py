import os
import json
import shutil
from pathlib import Path

import pytest
from docker import DockerClient


@pytest.fixture(scope='module')
def client():
    return DockerClient(base_url="tcp://localhost:2375", version="auto")


def test_run_container(client, test_path: Path):
    secret_path = test_path / 'secrets'
    secret_path.mkdir(exist_ok=True)

    with (secret_path / 'key.json').open(mode='w') as f:
        json.dump({"foo": "bar"}, f)

    container = client.containers.run(
        image="docker-image-local:latest",
        # name='docker-local',
        environment=["CALC_ASAT_DT=FOO"],
        # NOTE: Fix mode of mount file.
        # volumes={
        #     './secrets/key.json': {
        #         'bind': '/secret/key.json',
        #         'mode': 'ro',
        #     }
        # },
        # NOTE:
        # volumes={
        #     os.path.join(os.getcwd(), 'secrets'): {
        #         'bind': '/secret', 'mode': 'rw'
        #     }
        # },
        volumes={
            Path.cwd() / 'secrets': {
                'bind': '/secret', 'mode': 'rw'
            }
        },
        auto_remove=True,
        detach=True,
    )

    for line in container.logs(stream=True, timestamps=True):
        print(line.strip().decode())

    shutil.rmtree(secret_path)


def test_mount_volume(client):
    container = client.containers.run(
        image='ubuntu:latest',
        command='ls -ltr /tmp/tests',
        volumes={
            os.getcwd(): {'bind': '/tmp/tests', 'mode': 'rw'}
        },
        auto_remove=True,
        detach=True,
    )
    for line in container.logs(stream=True):
        print(line)

    lines = client.containers.run(
        'ubuntu:latest',
        'ls -la /',
        volumes={os.getcwd(): {'bind': '/tmp/', 'mode': 'rw'}},
        stream=True
    )
    for line in lines:
        print(line)


def test_catch_error(client):
    client.containers.get(container_id='test-raise-error-python').remove()

    container = client.containers.run(
        image='python:3.9-slim',
        name='test-raise-error-python',
        command='python -c "raise ValueError()"',
        auto_remove=False,
        detach=True,
    )
    for line in container.logs(stream=True):
        print(line)

    print(container.status)
    print(container.health)
    print(container.attrs["State"])

    result = container.wait()
    print(result)
    print(container.logs(stdout=False, stderr=True))
