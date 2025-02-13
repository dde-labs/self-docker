import os
import json
from pathlib import Path
from typing import Any

import pytest
import docker
from docker import DockerClient


@pytest.fixture(scope='module')
def client():
    return DockerClient(base_url="tcp://localhost:2375", version="auto")


def test_build(client, test_path: Path, docker_path: Path):
    image = client.api.build(
        path='..',
        dockerfile=str((docker_path / 'Dockerfile').resolve().absolute()),
        tag="docker-image-local:latest",
        quiet=False,
        decode=True,
        rm=True,
        nocache=True,
    )
    for line in image:
        print(line)


def test_build_by_object(test_path: Path, docker_path: Path):
    client = docker.from_env()

    with (docker_path / 'Dockerfile').open(mode='rb') as docker_file:
        image = client.api.build(
            path='..',
            fileobj=docker_file,
            custom_context=True,
            tag="poc-build-local:latest",
            quiet=False,
            decode=True,
        )

        for line in image:
            print(line)


def test_pull(client, gcloud_project_id: str):
    resp = client.api.pull(
        # https://asia-southeast1-docker.pkg.dev/v2/gcloud_project_id/ar-data360-docker/data360-de-push-gar-poc/manifests/latest
        repository=(
            f"asia-southeast1-docker.pkg.dev/{gcloud_project_id}/ar-data360-docker"
            f"/data360-de-push-gar-poc"
        ),
        tag="latest",
        stream=True,
        decode=True,
    )
    for line in resp:
        print(json.dumps(line, indent=4))


def test_pull_with_override_auth_conf(client, gcloud_project_id: str):
    resp = client.api.pull(
        repository=(
            f"asia-southeast1-docker.pkg.dev/{gcloud_project_id}/ar-data360-docker"
            f"/data360-de-push-gar-poc"
        ),
        tag="latest",
        auth_config={
            "username": "_json_key",
            "password": os.getenv('GOOGLE_CREDENTIAL'),
        },
        stream=True,
        decode=True,
    )
    for line in resp:
        print(json.dumps(line, indent=4))


def test_run_container(client, gcloud_project_id: str):
    container = client.containers.run(
        image=(
            f"asia-southeast1-docker.pkg.dev/{gcloud_project_id}/ar-data360-docker"
            f"/data360-de-push-gar-poc"
        ),
        name='unique_image_name',
        environment=["FOO=BAR"],
        volumes=["/secrets:/secret"],
        auto_remove=True,
        detach=True,
    )
    for line in container.logs(stream=True, timestamps=True):
        print(line.strip().decode())


def test_images(client):
    rs: list[dict[str, Any]] = client.api.images()
    print(type(rs))
    for img in rs:
        print(type(img))
        print(img)
