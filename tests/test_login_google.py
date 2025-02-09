import os
import json
import base64

import pytest
from docker import APIClient
from google.oauth2 import service_account


@pytest.fixture(scope='module')
def client():
    # NOTE: The base url is use the same value in the Docker Desktop setting
    #   page.
    return APIClient(base_url="tcp://localhost:2375", version="auto")


def test_login_to_google(client):
    rs = client.login(
        username="_json_key",
        password=os.getenv('GOOGLE_CREDENTIAL'),
        registry="asia-southeast1-docker.pkg.dev",
    )
    assert rs == {'IdentityToken': '', 'Status': 'Login Succeeded'}

    rs = client.pull(
        repository=(
            "asia-southeast1-docker.pkg.dev/scg-cbm-do-dev-rg/ar-data360-docker"
            "/data360-de-push-gar-poc"
        ),
        tag="latest",
    )
    print(type(rs))
    print(rs)


def test_login_to_google_base64(client):
    rs = client.login(
        username="_json_key_base64",
        password=(
            base64.b64encode(os.getenv('GOOGLE_CREDENTIAL').encode('utf-8'))
            .decode('utf-8')
        ),
        registry="asia-southeast1-docker.pkg.dev",
        email=None,
        reauth=True,
    )
    assert rs == {'IdentityToken': '', 'Status': 'Login Succeeded'}


def test_login_to_google_with_access_token(client):
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.getenv('GOOGLE_CREDENTIAL'))
    )
    rs = client.login(
        username="oauth2accesstoken",
        password=credentials.token,
        registry="asia-southeast1-docker.pkg.dev",
        email=None,
        reauth=True,
    )
    assert rs == {'IdentityToken': '', 'Status': 'Login Succeeded'}
