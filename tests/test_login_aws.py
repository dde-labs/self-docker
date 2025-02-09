import base64

import pytest
from docker import APIClient
import boto3


@pytest.fixture(scope='module')
def client():
    # NOTE: The base url is use the same value in the Docker Desktop setting
    #   page.
    return APIClient(base_url="tcp://localhost:2375", version="auto")


def test_login_to_aws_with_access_token(client):
    ecr_client = boto3.client(
        'ecr',
        aws_access_key_id="xyz",
        aws_secret_access_key="abc",
        region_name="ap-south-1"
    )
    token = ecr_client.get_authorization_token()["authorizationData"][0]
    client.login(
        username="AWS",
        password=(
            base64.b64decode(token["authorizationToken"])
            .decode()
            .split(":")
            [1]
        ),
        registry="xxxx.dkr.ecr.ap-south-1.amazonaws.com"
    )
