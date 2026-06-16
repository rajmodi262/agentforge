"""AgentForge AI — Integration Tests

End-to-end tests for the full pipeline:
register → create project → start workflow → check results → download report

Uses fixtures from conftest.py (setup_database, client, auth_headers, etc.)
"""

import pytest


# ─────────────────────────────── Auth Tests ───────────────────────────────

class TestAuth:
    def test_register_success(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "new@test.com",
            "password": "SecurePass1",
            "name": "New User"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client):
        payload = {"email": "dup@test.com", "password": "SecurePass1"}
        client.post("/api/v1/auth/register", json=payload)
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_weak_password(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "weak@test.com",
            "password": "short"
        })
        assert resp.status_code == 422  # Pydantic validation error

    def test_login_success(self, client):
        # Register first
        client.post("/api/v1/auth/register", json={
            "email": "login@test.com",
            "password": "LoginPass1"
        })
        # Login
        resp = client.post("/api/v1/auth/login", json={
            "email": "login@test.com",
            "password": "LoginPass1"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/register", json={
            "email": "wrong@test.com",
            "password": "CorrectPass1"
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "wrong@test.com",
            "password": "WrongPass1"
        })
        assert resp.status_code == 401

    def test_get_me(self, client, auth_headers):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@agentforge.ai"

    def test_get_me_no_token(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401


# ─────────────────────────────── Project Tests ───────────────────────────────

class TestProjects:
    def test_create_project(self, client, auth_headers):
        resp = client.post("/api/v1/projects/", json={
            "title": "AI Food Delivery",
            "business_idea": "An AI-powered food delivery platform that predicts what users want to eat",
            "target_market": "India",
            "budget_range": "₹5-10 lakhs"
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "AI Food Delivery"
        assert data["status"] == "draft"

    def test_list_projects(self, client, auth_headers):
        for title in ["Project A", "Project B"]:
            client.post("/api/v1/projects/", json={
                "title": title,
                "business_idea": f"A platform for {title.lower()} that solves important problems",
            }, headers=auth_headers)
        
        resp = client.get("/api/v1/projects/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_get_project(self, client, auth_headers):
        create_resp = client.post("/api/v1/projects/", json={
            "title": "Test Get",
            "business_idea": "Testing the get endpoint for individual projects",
        }, headers=auth_headers)
        project_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == project_id

    def test_create_project_validation(self, client, auth_headers):
        resp = client.post("/api/v1/projects/", json={
            "title": "Bad",
            "business_idea": "short",
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_project_isolation(self, client):
        """Projects from different users should be isolated."""
        resp_a = client.post("/api/v1/auth/register", json={
            "email": "usera@test.com", "password": "PassA1234"
        })
        headers_a = {"Authorization": f"Bearer {resp_a.json()['access_token']}"}

        resp_b = client.post("/api/v1/auth/register", json={
            "email": "userb@test.com", "password": "PassB1234"
        })
        headers_b = {"Authorization": f"Bearer {resp_b.json()['access_token']}"}

        client.post("/api/v1/projects/", json={
            "title": "A's Project",
            "business_idea": "User A's private business idea for testing",
        }, headers=headers_a)

        resp = client.get("/api/v1/projects/", headers=headers_b)
        assert resp.json()["total"] == 0


# ─────────────────────────────── Results Tests ───────────────────────────────

class TestResults:
    def test_results_no_workflow(self, client, auth_headers):
        create_resp = client.post("/api/v1/projects/", json={
            "title": "No Workflow",
            "business_idea": "A project that has not been run through the pipeline yet",
        }, headers=auth_headers)
        project_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/projects/{project_id}/results", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "no_workflow"
        assert data["agents"] == {}

    def test_status_no_workflow(self, client, auth_headers):
        create_resp = client.post("/api/v1/projects/", json={
            "title": "No Workflow Status",
            "business_idea": "Testing the status endpoint before any workflow runs",
        }, headers=auth_headers)
        project_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/projects/{project_id}/status", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "no_workflow"


# ─────────────────────────────── Health Tests ───────────────────────────────

class TestHealth:
    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "AgentForge AI"
        assert data["version"] == "1.0.0"

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "ai_provider" in data


# ─────────────────────────────── Input Sanitization Tests ───────────────────────────────

class TestSanitization:
    def test_html_injection_blocked(self, client, auth_headers):
        resp = client.post("/api/v1/projects/", json={
            "title": "<script>alert('xss')</script>My Project",
            "business_idea": "<img src=x onerror=alert(1)> A real business idea about food delivery",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "<script>" not in data["title"]
        assert "<img" not in data["business_idea"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
