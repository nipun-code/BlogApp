from fastapi import status
from database.models import TokenBlacklist


class TestSignup:
    def test_signup_success(self, client):
        response = client.post(
            "/api/auth/signup",
            json={"email": "newuser@example.com", "password": "password123"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_duplicate_email(self, client, test_user):
        response = client.post(
            "/api/auth/signup",
            json={"email": test_user.email, "password": "password123"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_signup_invalid_email(self, client):
        response = client.post(
            "/api/auth/signup",
            json={"email": "invalid-email", "password": "password123"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_short_password(self, client):
        response = client.post(
            "/api/auth/signup",
            json={"email": "newuser@example.com", "password": "12345"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSignin:
    def test_signin_success(self, client, test_user):
        response = client.post(
            "/api/auth/signin",
            json={"email": test_user.email, "password": "password123"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_signin_wrong_password(self, client, test_user):
        response = client.post(
            "/api/auth/signin",
            json={"email": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_signin_nonexistent_user(self, client):
        response = client.post(
            "/api/auth/signin",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshToken:
    def test_refresh_token_success(self, client, refresh_token):
        response = client.post(
            "/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_with_access_token(self, client, auth_token):
        response = client.post(
            "/api/auth/refresh", headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_with_invalid_token(self, client):
        response = client.post(
            "/api/auth/refresh", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_blacklisted_token(
        self, client, refresh_token, test_user, db_session
    ):
        blacklist_entry = TokenBlacklist(token=refresh_token, user_id=test_user.id)
        db_session.add(blacklist_entry)
        db_session.commit()
        response = client.post(
            "/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    def test_logout_success(self, client, auth_headers):
        response = client.post("/api/auth/logout", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "logged out" in response.json()["message"].lower()

    def test_logout_without_token(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout_with_invalid_token(self, client):
        response = client.post(
            "/api/auth/logout", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
