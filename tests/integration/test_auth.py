from models import User

def test_register_and_login(client):
    """
    GIVEN a Flask application configured for testing
    WHEN a new user is registered and then logs in
    THEN check that the registration and login are successful
    """
    # Test user registration
    register_response = client.post("/api/register", json={
        "name": "Test Teacher",
        "email": "teacher@test.com",
        "password": "password123",
        "role": "teacher"
    })
    assert register_response.status_code == 201

    # Test user login
    login_response = client.post("/api/login", json={
        "email": "teacher@test.com",
        "password": "password123"
    })
    assert login_response.status_code == 200
    
    data = login_response.get_json()
    assert data["user"]["email"] == "teacher@test.com"
    assert data["user"]["role"] == "teacher"

def test_login_with_invalid_credentials(client):
    """
    GIVEN a registered user
    WHEN the user tries to log in with an incorrect password
    THEN check that the login fails
    """
    # Register a user first
    client.post("/api/register", json={
        "name": "Another Teacher",
        "email": "teacher2@test.com",
        "password": "password123",
        "role": "teacher"
    })
    
    # Attempt to log in with the wrong password
    login_response = client.post("/api/login", json={
        "email": "teacher2@test.com",
        "password": "wrongpassword"
    })
    assert login_response.status_code == 401
    
    data = login_response.get_json()
    assert data["error"] == "Invalid email or password" 