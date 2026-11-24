import pytest
from fastapi.testclient import TestClient

from app import create_app
from limits import Limiter
from store import MemoryStore

TOKEN = "s3cret"


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def store():
    return MemoryStore()


@pytest.fixture
def client(store, clock):
    limiter = Limiter(global_per_min=30, per_client_per_min=5, trust_forwarded_for=False, clock=clock)
    return TestClient(create_app(store, TOKEN, limiter))
