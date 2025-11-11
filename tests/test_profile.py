from fastapi import status


class TestGetProfile:
    def test_get_profile_success(self, client, auth_headers, test_user):
        response = client.get("/api/profile", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert data["id"] == test_user.id

    def test_get_profile_without_auth(self, client):
        response = client.get("/api/profile")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_profile_invalid_token(self, client):
        response = client.get(
            "/api/profile", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateProfile:
    def test_update_profile_all_fields(self, client, auth_headers):
        """Test updating all profile fields"""
        profile_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "mobile": "9876543210",
            "picture": "https://example.com/pic.jpg",
            "country": "India",
        }

        response = client.put("/api/profile", headers=auth_headers, json=profile_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == profile_data["first_name"]
        assert data["last_name"] == profile_data["last_name"]
        assert data["mobile"] == profile_data["mobile"]
        assert data["country"] == profile_data["country"]

    def test_update_profile_partial(self, client, auth_headers):
        response = client.put(
            "/api/profile", headers=auth_headers, json={"first_name": "NewName"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "NewName"

    def test_update_profile_without_auth(self, client):
        response = client.put("/api/profile", json={"first_name": "NewName"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_profile_empty_data(self, client, auth_headers):
        response = client.put("/api/profile", headers=auth_headers, json={})

        assert response.status_code == status.HTTP_200_OK
