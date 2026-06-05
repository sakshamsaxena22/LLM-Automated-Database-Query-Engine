import os
import importlib

from fastapi.testclient import TestClient


os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/payments")
os.environ.setdefault("GROQ_API_KEY", "dummy_key_for_tests")
os.environ.setdefault("MAX_RESULTS", "100")


class DummyCursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, _sort):
        return self

    def limit(self, limit):
        return self._docs[:limit]


class DummyCollection:
    def __init__(self):
        class Admin:
            @staticmethod
            def command(_name):
                return {"ok": 1}

        class Client:
            admin = Admin()

        class Database:
            client = Client()

        self.database = Database()

    def find(self, *_args, **_kwargs):
        return DummyCursor(
            [
                {
                    "_id": "abc123",
                    "transaction_id": "TXN000001",
                    "status": "FAILED",
                }
            ]
        )


main = importlib.import_module("app.main")
routes = importlib.import_module("app.routes")


def test_query_endpoint_returns_results(monkeypatch):
    monkeypatch.setattr(
        routes,
        "generate_query",
        lambda _q: {"filter": {"status": "FAILED"}, "limit": 10},
    )
    monkeypatch.setattr(routes, "collection", DummyCollection())

    client = TestClient(main.app)
    response = client.post("/query", json={"query": "show failed transactions"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["generated_query"]["filter"] == {"status": "FAILED"}
    assert payload["results"][0]["transaction_id"] == "TXN000001"
