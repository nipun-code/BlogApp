from services.user_service import UserService
from services.blog_service import BlogService
from schemas.user import UserSignup, UserProfileUpdate
from schemas.blog import BlogCreate, BlogUpdate
from auth.password import verify_password


class TestUserService:
    def test_create_user(self, db_session):
        user_data = UserSignup(email="new@example.com", password="password123")
        user = UserService.create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == user_data.email
        assert verify_password("password123", user.hashed_password)

    def test_get_user_by_email(self, db_session, test_user):
        user = UserService.get_user_by_email(db_session, test_user.email)

        assert user is not None
        assert user.id == test_user.id

    def test_authenticate_user_success(self, db_session, test_user):
        user = UserService.authenticate_user(db_session, test_user.email, "password123")

        assert user is not None
        assert user.id == test_user.id

    def test_authenticate_user_wrong_password(self, db_session, test_user):
        user = UserService.authenticate_user(
            db_session, test_user.email, "wrongpassword"
        )

        assert user is None

    def test_update_profile(self, db_session, test_user):
        profile_data = UserProfileUpdate(first_name="Updated", country="Canada")

        updated_user = UserService.update_profile(db_session, test_user, profile_data)

        assert updated_user.first_name == "Updated"
        assert updated_user.country == "Canada"

    def test_generate_tokens(self, test_user):
        access_token, refresh_token = UserService.generate_tokens(test_user.id)

        assert access_token is not None
        assert refresh_token is not None
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)


class TestBlogService:
    def test_create_blog(self, db_session, test_user):
        blog_data = BlogCreate(
            title="Test Blog", content="Test Content", category="Tech"
        )

        blog = BlogService.create_blog(db_session, blog_data, test_user.id)

        assert blog.id is not None
        assert blog.title == blog_data.title
        assert blog.author_id == test_user.id

    def test_get_blog_by_id(self, db_session, test_blog):
        blog = BlogService.get_blog_by_id(db_session, test_blog.id)

        assert blog is not None
        assert blog.id == test_blog.id

    def test_get_recent_blogs(self, db_session, multiple_blogs):
        blogs = BlogService.get_recent_blogs(db_session, skip=0, limit=10)
        assert len(blogs) == 4
        assert blogs[0].created_at >= blogs[-1].created_at

    def test_get_blogs_by_category(self, db_session, multiple_blogs):
        blogs = BlogService.get_blogs_by_category(db_session, "Technology")

        assert len(blogs) == 2
        assert all(blog.category == "Technology" for blog in blogs)

    def test_search_blogs(self, db_session, multiple_blogs):
        blogs = BlogService.search_blogs(db_session, "Python")

        assert len(blogs) >= 1
        assert any("Python" in blog.title for blog in blogs)

    def test_update_blog(self, db_session, test_blog):
        blog_data = BlogUpdate(title="Updated Title")

        updated_blog = BlogService.update_blog(db_session, test_blog, blog_data)

        assert updated_blog.title == "Updated Title"
        assert updated_blog.content == test_blog.content

    def test_delete_blog(self, db_session, test_blog):
        blog_id = test_blog.id
        BlogService.delete_blog(db_session, test_blog)

        deleted_blog = BlogService.get_blog_by_id(db_session, blog_id)
        assert deleted_blog is None
