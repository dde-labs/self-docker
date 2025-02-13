from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from datetime import datetime

from docker import DockerClient
from docker.errors import ContainerError
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient, KeyVaultSecret

from .utils import ConfigEnv, read_env, read_extended_prop, write_output, \
    run_monitoring


def secret_client(name: str) -> SecretClient:
    return SecretClient(
        vault_url=f"https://{name}.vault.azure.net",
        credential=ManagedIdentityCredential()
    )


def set_credential(env: ConfigEnv) -> KeyVaultSecret:
    """Setting credential from Azure Key Vault."""
    sc: SecretClient = secret_client(env.kv_name)
    google_gar_credential: KeyVaultSecret = sc.get_secret(
        name="google-gcr-sa-json")
    google_secret_credential: KeyVaultSecret = sc.get_secret(
        name="google-secret-sa-json")

    secret_path: Path = Path('./secrets')
    secret_path.mkdir(exist_ok=True)

    with (secret_path / 'secret.json').open(mode='w', encoding='utf-8') as f:
        json.dump(json.loads(google_secret_credential.value), f)

    print("Create secrets/secret.json on the local storage successful.")
    return google_gar_credential


def run_docker(
    credential: KeyVaultSecret,
    region_name: str,
    project_id: str,
    service_name: str,
    image: str,
    tag: str,
    env_vars: list[str],
) -> None:
    """Run the Docker container."""
    client = DockerClient(base_url="unix://var/run/docker.sock", version="auto")
    print(client.version())

    resp = client.api.pull(
        repository=f"{region_name}-docker.pkg.dev/{project_id}/{service_name}/{image}",
        tag=tag,
        auth_config={
            "username": "_json_key",
            "password": credential.value,
        },
        stream=True,
        decode=True,
    )
    for line in resp:
        print(line)

    unique_image_name: str = f"{image}_{datetime.now():%Y%m%d%H%M%S}"
    container = client.containers.run(
        image=f"{region_name}-docker.pkg.dev/{project_id}/{service_name}/{image}:{tag}",
        name=unique_image_name,
        environment=env_vars,
        volumes={
            Path.cwd() / 'secrets': {
                'bind': '/secrets',
                'mode': 'rw',
            },
        },
        detach=True,
    )

    for line in container.logs(stream=True, timestamps=True):
        print(line.strip().decode())

    # NOTE: This code copy from the `docker` package.
    exit_status: int = container.wait()['StatusCode']
    if exit_status != 0:
        out = container.logs(stdout=False, stderr=True)
        container.remove()
        raise ContainerError(
            container,
            exit_status,
            None,
            f"{region_name}-docker.pkg.dev/{project_id}/{service_name}/{image}:{tag}",
            out,
        )


def main() -> None:
    env: ConfigEnv = read_env("env.json")
    credential: KeyVaultSecret = set_credential(env=env)

    extended_prop: dict[str, Any] = read_extended_prop()
    process_obj: dict[str, Any] = extended_prop.get("PRCS_OBJ")

    # NOTE: Import parameter from the process object.
    service_name: str = process_obj.get("SERVICE_NM", "ar-data360-docker")
    full_image_name: str = process_obj.get(
        "IMAGE_NM", "image-gar-poc:latest"
    )
    params_mapping: str = process_obj.get("PARAMS", "")

    # NOTE: Prepare parameters.
    image_name, tag = full_image_name.split(':', maxsplit=1)

    # NOTE: Params string: `source:target^|source:target`
    env_params: list[str] = [
        f"{e[1]}={process_obj[e[0]]}"
        for e in map(lambda p: p.split(':', maxsplit=1),
                     params_mapping.strip().split('^|'))
        if len(e) == 2 and e[0] in process_obj
    ]

    run_docker(
        credential,
        region_name=env.google_region_name,
        project_id=env.google_project_id,
        service_name=service_name,
        image=image_name,
        tag=tag,
        env_vars=[
            f"ENV={env.env}",
            "SECRET_FILENAME=secrets/secret.json",
            *env_params,
        ],
    )

    write_output(data={'extendedProperties': extended_prop})
    return None


if __name__ == "__main__":
    run_monitoring(main_func=main)
