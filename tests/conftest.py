import os
import pytest
from mbtest.server import MountebankServer
from dotenv import dotenv_values


@pytest.fixture(scope="session")
def config():
    """Loads test environment variables from .env.test file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env.test')
    return dotenv_values(env_path)


@pytest.fixture(scope="session")
def mock_server(config):
    """Creates a handle for the mountebank server that must be running in the background."""
    host = config["mb_server_host"]
    port = int(config['mb_server_port'])
    return MountebankServer(host=host, port=port)
