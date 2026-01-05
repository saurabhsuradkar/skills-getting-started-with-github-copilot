"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    from app import activities
    initial_state = {
        "Tennis Club": {
            "description": "Develop tennis skills and compete in friendly matches",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join our competitive basketball team",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucy@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in school concerts",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["william@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    yield
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Tennis Club" in data
        assert "Basketball Team" in data

    def test_activities_structure(self, client, reset_activities):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Tennis Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_activities_have_correct_participants(self, client, reset_activities):
        """Test that participants are loaded correctly"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Tennis Club"]["participants"]
        assert "james@mergington.edu" in data["Basketball Team"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newemail@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        new_email = "test@mergington.edu"
        client.post(f"/activities/Tennis%20Club/signup?email={new_email}")
        
        response = client.get("/activities")
        data = response.json()
        assert new_email in data["Tennis Club"]["participants"]

    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup to non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_signed_up(self, client, reset_activities):
        """Test signup when already registered"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_fills_spots(self, client, reset_activities):
        """Test that signup respects max participants limit by checking count"""
        response = client.get("/activities")
        activity_before = response.json()["Tennis Club"]
        initial_count = len(activity_before["participants"])
        
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        response = client.get("/activities")
        activity_after = response.json()["Tennis Club"]
        assert len(activity_after["participants"]) == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Tennis%20Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert "alex@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.delete(
            "/activities/Tennis%20Club/unregister?email=alex@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Tennis Club"]["participants"]

    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_participant(self, client, reset_activities):
        """Test unregister when not a participant"""
        response = client.delete(
            "/activities/Tennis%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not found in this activity" in response.json()["detail"]

    def test_unregister_then_can_signup_again(self, client, reset_activities):
        """Test that after unregistering, student can sign up again"""
        email = "alex@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Tennis%20Club/unregister?email={email}")
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()["Tennis Club"]["participants"]
        
        # Sign up again
        response = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()["Tennis Club"]["participants"]


class TestIntegration:
    """Integration tests combining multiple operations"""

    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete workflow of signup and unregister"""
        email = "integration@mergington.edu"
        activity = "Basketball%20Team"
        
        # Verify not in list
        response = client.get("/activities")
        assert email not in response.json()["Basketball Team"]["participants"]
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in list
        response = client.get("/activities")
        assert email in response.json()["Basketball Team"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify not in list
        response = client.get("/activities")
        assert email not in response.json()["Basketball Team"]["participants"]

    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        activity = "Art%20Studio"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Art Studio"]["participants"]
