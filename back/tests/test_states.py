from fastapi.testclient import TestClient

from back.tests.conftest import DictStorage


def test_state_router(tickers: list[str], client: TestClient, storage: DictStorage):
    for ticker in tickers:
        resp = client.get(f'ticker/v1/{ticker}/').json()

        assert len(resp) > 0

