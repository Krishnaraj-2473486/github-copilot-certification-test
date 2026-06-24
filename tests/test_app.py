import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the original activities state for resetting between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to their original state before and after each test."""
    # Reset before test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    # Reset after test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities (Arrange-Act-Assert)."""
        # Arrange: no special setup required (fixture provides `client`)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9


class TestSignupForActivity:
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity (Arrange-Act-Assert)."""
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for Chess Club"
        assert email in activities["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist (Arrange-Act-Assert)."""
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_signed_up(self, client):
        """Test signup when student is already signed up (Arrange-Act-Assert)."""
        # Arrange
        email = "michael@mergington.edu"  # already present in fixture data

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"

    def test_signup_checks_activity_existence_first(self, client):
        """Test that activity existence is checked before participant status (Arrange-Act-Assert)."""
        # Arrange
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregisterFromActivity:
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity (Arrange-Act-Assert)."""
        # Arrange
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from Chess Club"
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist (Arrange-Act-Assert)."""
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_in_activity(self, client):
        """Test unregistration when student is not in the activity (Arrange-Act-Assert)."""
        # Arrange
        email = "notastudet@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in activity"
