import os
from pathlib import Path
from dotenv import load_dotenv

import pytest


load_dotenv(Path(__file__).parent.parent / '.env')


@pytest.fixture(scope='session')
def test_path() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope='session')
def docker_path(test_path) -> Path:
    return test_path.parent / '.container'


@pytest.fixture(scope='session')
def gcloud_project_id() -> str:
    return os.getenv('GOOGLE_PROJECT_ID')
