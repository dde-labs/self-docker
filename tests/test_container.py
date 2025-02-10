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
        name='docker-local',
        environment=["FOO=BAR"],
        volumes=["/secrets:/secret"],
        auto_remove=True,
        detach=True,
    )
    for line in container.logs(stream=True, timestamps=True):
        print(line.strip().decode())

    shutil.rmtree(secret_path)
