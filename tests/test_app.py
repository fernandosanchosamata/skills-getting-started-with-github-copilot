import copy
import os
import sys
from urllib.parse import quote

# Make src/ importable from the repository root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import app as app_module

from fastapi.testclient import TestClient
import pytest

original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(original_activities)
    yield


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(existing_email)}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "james@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "ghoststudent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
