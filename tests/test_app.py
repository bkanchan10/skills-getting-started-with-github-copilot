from fastapi.testclient import TestClient
import sys

# Ensure src is importable
sys.path.append("src")

from app import app


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    # Expect a dictionary of activities
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_and_unregister_flow():
    activity = "Basketball Team"
    email = "pytest_user@example.com"

    # Ensure not already registered
    before = client.get("/activities").json()
    if email in before[activity]["participants"]:
        # remove if present to ensure test idempotence
        client.post(f"/activities/{activity}/unregister", params={"email": email})

    # Sign up
    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # Verify participant present
    res2 = client.get("/activities")
    assert res2.status_code == 200
    assert email in res2.json()[activity]["participants"]

    # Unregister
    res3 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert res3.status_code == 200
    assert "Unregistered" in res3.json().get("message", "")

    # Verify removed
    res4 = client.get("/activities")
    assert email not in res4.json()[activity]["participants"]
