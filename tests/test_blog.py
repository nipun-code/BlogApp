from fastapi import status
from auth.jwt_handler import create_access_token


class TestCreateBlog:
    def test_create_blog_success(self, client, auth_headers):
        blog_data = {
            "title": "New Blog Post",
            "content": "This is the content of the blog post",
            "category": "Technology",
        }

        response = client.post("/api/blogs", headers=auth_headers, json=blog_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == blog_data["title"]
        assert data["content"] == blog_data["content"]
        assert data["category"] == blog_data["category"]
        assert "id" in data
        assert "created_at" in data

    def test_create_blog_without_auth(self, client):
        blog_data = {"title": "New Blog Post", "content": "Content", "category": "Tech"}

        response = client.post("/api/blogs", json=blog_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_blog_missing_fields(self, client, auth_headers):
        response = client.post(
            "/api/blogs", headers=auth_headers, json={"title": "Only Title"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListBlogs:
    def test_list_blogs_success(self, client, multiple_blogs):
        response = client.get("/api/blogs")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4

    def test_list_blogs_pagination(self, client, multiple_blogs):
        response = client.get("/api/blogs?skip=1&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_blogs_empty(self, client):
        response = client.get("/api/blogs")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestGetBlog:
    def test_get_blog_success(self, client, test_blog):
        response = client.get(f"/api/blogs/{test_blog.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_blog.id
        assert data["title"] == test_blog.title
        assert data["content"] == test_blog.content

    def test_get_blog_not_found(self, client):
        response = client.get("/api/blogs/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListBlogsByCategory:
    def test_list_by_category_success(self, client, multiple_blogs):
        response = client.get("/api/blogs/category/Technology")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(blog["category"] == "Technology" for blog in data)

    def test_list_by_category_empty(self, client, multiple_blogs):
        response = client.get("/api/blogs/category/NonExistent")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestSearchBlogs:
    def test_search_blogs_by_title(self, client, multiple_blogs):
        response = client.get("/api/blogs/search?q=Python")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert "Python" in data[0]["title"]

    def test_search_blogs_by_content(self, client, multiple_blogs):
        response = client.get("/api/blogs/search?q=blog post 1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_search_blogs_case_insensitive(self, client, multiple_blogs):
        response = client.get("/api/blogs/search?q=python")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

    def test_search_blogs_no_results(self, client, multiple_blogs):
        response = client.get("/api/blogs/search?q=nonexistentterm")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_search_blogs_missing_query(self, client):
        response = client.get("/api/blogs/search")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateBlog:
    def test_update_blog_success(self, client, auth_headers, test_blog):
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "category": "Science",
        }

        response = client.put(
            f"/api/blogs/{test_blog.id}", headers=auth_headers, json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["category"] == update_data["category"]

    def test_update_blog_partial(self, client, auth_headers, test_blog):
        response = client.put(
            f"/api/blogs/{test_blog.id}",
            headers=auth_headers,
            json={"title": "Only Title Updated"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Only Title Updated"
        assert data["content"] == test_blog.content

    def test_update_blog_unauthorized(self, client, test_blog, test_user_2):
        other_user_token = create_access_token(test_user_2.id)
        headers = {"Authorization": f"Bearer {other_user_token}"}

        response = client.put(
            f"/api/blogs/{test_blog.id}", headers=headers, json={"title": "Hacked"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_blog_not_found(self, client, auth_headers):
        response = client.put(
            "/api/blogs/99999", headers=auth_headers, json={"title": "New Title"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_blog_without_auth(self, client, test_blog):
        """Test updating blog without authentication"""
        response = client.put(f"/api/blogs/{test_blog.id}", json={"title": "New Title"})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteBlog:
    def test_delete_blog_success(self, client, auth_headers, test_blog):
        response = client.delete(f"/api/blogs/{test_blog.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify blog is deleted
        get_response = client.get(f"/api/blogs/{test_blog.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_blog_unauthorized(self, client, test_blog, test_user_2):
        other_user_token = create_access_token(test_user_2.id)
        headers = {"Authorization": f"Bearer {other_user_token}"}

        response = client.delete(f"/api/blogs/{test_blog.id}", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_blog_not_found(self, client, auth_headers):
        response = client.delete("/api/blogs/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_blog_without_auth(self, client, test_blog):
        response = client.delete(f"/api/blogs/{test_blog.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
