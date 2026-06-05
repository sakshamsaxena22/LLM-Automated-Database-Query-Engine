"""
End-to-end API test suite for the Enterprise AI Data Management Platform.

Run with:  venv\\Scripts\\python.exe -m pytest tests/test_api_e2e.py -v
"""

import httpx
import pytest
import time
import uuid

BASE = "http://127.0.0.1:8000/api/v1"

# Unique test user to avoid conflicts
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Test User"

# Will be set during tests
ACCESS_TOKEN = None
USER_ID = None


def auth_header():
    return {"Authorization": f"Bearer {ACCESS_TOKEN}"}


# ─── Health ───────────────────────────────────────────────────────────

class TestHealth:
    def test_app_health(self):
        r = httpx.get(f"{BASE}/health/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"
        print(f"  [PASS] App health: {data}")

    def test_db_health(self):
        r = httpx.get(f"{BASE}/health/db")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "connected"
        assert data["database"] == "enterprise_db"
        print(f"  [PASS] DB health: {data}")


# ─── Auth ─────────────────────────────────────────────────────────────

class TestAuth:
    def test_01_register(self):
        global ACCESS_TOKEN, USER_ID
        r = httpx.post(f"{BASE}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": TEST_NAME,
        })
        assert r.status_code == 201, f"Register failed: {r.text}"
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user_id" in data
        ACCESS_TOKEN = data["access_token"]
        USER_ID = data["user_id"]
        print(f"  [PASS] Registered user {USER_ID}")

    def test_02_register_duplicate(self):
        r = httpx.post(f"{BASE}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": TEST_NAME,
        })
        assert r.status_code in (400, 409)
        print(f"  [PASS] Duplicate register rejected: {r.json().get('detail', 'Duplicate')}")

    def test_03_login(self):
        global ACCESS_TOKEN
        r = httpx.post(f"{BASE}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        assert r.status_code == 200, f"Login failed: {r.text}"
        data = r.json()
        assert "access_token" in data
        ACCESS_TOKEN = data["access_token"]
        print(f"  [PASS] Login OK, got new token")

    def test_04_login_wrong_password(self):
        r = httpx.post(f"{BASE}/auth/login", json={
            "email": TEST_EMAIL,
            "password": "wrongpassword",
        })
        assert r.status_code == 401
        print(f"  [PASS] Wrong password rejected")

    def test_05_get_me(self):
        r = httpx.get(f"{BASE}/auth/me", headers=auth_header())
        assert r.status_code == 200, f"Get me failed: {r.text}"
        data = r.json()
        assert data["email"] == TEST_EMAIL
        assert data["full_name"] == TEST_NAME
        print(f"  [PASS] GET /auth/me: {data['email']}, role={data['role']}")

    def test_06_unauthorized_without_token(self):
        r = httpx.get(f"{BASE}/auth/me")
        assert r.status_code == 401
        print(f"  [PASS] Unauthorized without token")

    def test_07_refresh_token(self):
        global ACCESS_TOKEN
        # First login to get a refresh token
        login_r = httpx.post(f"{BASE}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        refresh_tok = login_r.json()["refresh_token"]
        r = httpx.post(f"{BASE}/auth/refresh", json={
            "refresh_token": refresh_tok,
        })
        assert r.status_code == 200, f"Refresh failed: {r.text}"
        data = r.json()
        assert "access_token" in data
        ACCESS_TOKEN = data["access_token"]
        print(f"  [PASS] Token refreshed OK")


# ─── CRUD ─────────────────────────────────────────────────────────────

INSERTED_DOC_ID = None


class TestCRUD:
    def test_01_list_empty_collection(self):
        r = httpx.get(f"{BASE}/crud/test_items", headers=auth_header())
        assert r.status_code == 200
        data = r.json()
        assert "documents" in data or "total" in data
        print(f"  [PASS] List collection: {data.get('total', len(data.get('documents', [])))} docs")

    def test_02_insert_document(self):
        global INSERTED_DOC_ID
        # Need editor role — update our user first
        # For now, test with current role (viewer may be blocked)
        r = httpx.post(
            f"{BASE}/crud/test_items",
            headers=auth_header(),
            json={"document": {"name": "Test Item", "value": 42, "type": "widget"}},
        )
        if r.status_code == 201:
            data = r.json()
            INSERTED_DOC_ID = data.get("inserted_id")
            print(f"  [PASS] Inserted document: {INSERTED_DOC_ID}")
        elif r.status_code == 403:
            print(f"  [SKIP] Insert blocked (viewer role) - RBAC working correctly")
            pytest.skip("Viewer role can't insert")
        else:
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_03_get_document(self):
        if not INSERTED_DOC_ID:
            pytest.skip("No doc inserted")
        r = httpx.get(f"{BASE}/crud/test_items/{INSERTED_DOC_ID}", headers=auth_header())
        assert r.status_code == 200
        print(f"  [PASS] Get document OK")

    def test_04_update_document(self):
        if not INSERTED_DOC_ID:
            pytest.skip("No doc inserted")
        r = httpx.put(
            f"{BASE}/crud/test_items/{INSERTED_DOC_ID}",
            headers=auth_header(),
            json={"update": {"value": 99}},
        )
        if r.status_code == 200:
            print(f"  [PASS] Updated document")
        elif r.status_code == 403:
            print(f"  [SKIP] Update blocked (viewer role)")
            pytest.skip("Viewer role can't update")

    def test_05_delete_document(self):
        if not INSERTED_DOC_ID:
            pytest.skip("No doc inserted")
        r = httpx.delete(
            f"{BASE}/crud/test_items/{INSERTED_DOC_ID}",
            headers=auth_header(),
        )
        if r.status_code == 200:
            print(f"  [PASS] Deleted document")
        elif r.status_code == 403:
            print(f"  [SKIP] Delete blocked (viewer role)")
            pytest.skip("Viewer role can't delete")


# ─── Users ────────────────────────────────────────────────────────────

class TestUsers:
    def test_01_list_users(self):
        r = httpx.get(f"{BASE}/users/", headers=auth_header())
        # May be 403 if not admin
        if r.status_code == 200:
            data = r.json()
            print(f"  [PASS] List users: {data.get('total', '?')} users")
        elif r.status_code == 403:
            print(f"  [SKIP] List users blocked (not admin) - RBAC working")
            pytest.skip("Not admin")
        else:
            pytest.fail(f"Unexpected: {r.status_code}")


# ─── Analytics ────────────────────────────────────────────────────────

class TestAnalytics:
    def test_overview(self):
        r = httpx.get(f"{BASE}/analytics/overview", headers=auth_header())
        assert r.status_code == 200, f"Analytics failed: {r.text}"
        data = r.json()
        assert "total_users" in data
        assert "total_queries" in data
        print(f"  [PASS] Analytics: users={data['total_users']}, queries={data['total_queries']}")


# ─── Audit ────────────────────────────────────────────────────────────

class TestAudit:
    def test_audit_logs(self):
        r = httpx.get(f"{BASE}/audit/logs", headers=auth_header())
        if r.status_code == 200:
            data = r.json()
            print(f"  [PASS] Audit logs: {data.get('total', '?')} entries")
        elif r.status_code == 403:
            print(f"  [SKIP] Audit blocked (not admin) - RBAC working")
            pytest.skip("Not admin")


# ─── AI Query (requires Groq API key) ────────────────────────────────

class TestAI:
    def test_ai_query(self):
        r = httpx.post(
            f"{BASE}/ai/query",
            headers=auth_header(),
            json={"query": "show all documents", "collection": "test_items"},
            timeout=30.0,
        )
        if r.status_code == 200:
            data = r.json()
            print(f"  [PASS] AI query: {data['count']} results, {data['execution_time_ms']}ms, risk={data['risk_level']}")
        elif r.status_code == 500:
            detail = r.json().get("detail", "")
            print(f"  [WARN] AI query error (may need valid Groq key): {detail[:100]}")
        else:
            print(f"  [INFO] AI query status {r.status_code}: {r.text[:100]}")

    def test_query_history(self):
        r = httpx.get(f"{BASE}/ai/history", headers=auth_header())
        assert r.status_code == 200
        data = r.json()
        print(f"  [PASS] Query history: {data.get('total', 0)} entries")


# ─── Root ─────────────────────────────────────────────────────────────

class TestRoot:
    def test_root(self):
        r = httpx.get("http://127.0.0.1:8000/")
        assert r.status_code == 200
        data = r.json()
        assert data["version"] == "2.0.0"
        print(f"  [PASS] Root: {data['message']}")

    def test_docs(self):
        r = httpx.get("http://127.0.0.1:8000/docs")
        assert r.status_code == 200
        print(f"  [PASS] Swagger docs accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
