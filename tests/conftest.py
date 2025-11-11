import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import app
from database.connection import Base, get_db
from database.models import User, Blog
from auth.password import hash_password
from auth.jwt_handler import create_access_token, create_refresh_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="User",
        mobile="1234567890",
        country="INDIA",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_2(db_session):
    user = User(
        email="user2@example.com",
        hashed_password=hash_password("password123"),
        first_name="User",
        last_name="Two",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    return create_access_token(test_user.id)


@pytest.fixture
def refresh_token(test_user):
    return create_refresh_token(test_user.id)


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_blog(db_session, test_user):
    blog = Blog(
        title="Test Blog Post",
        content="This is a test blog content",
        category="Technology",
        author_id=test_user.id,
    )
    db_session.add(blog)
    db_session.commit()
    db_session.refresh(blog)
    return blog


@pytest.fixture
def multiple_blogs(db_session, test_user):
    blogs = []
    categories = ["Technology", "Science", "Health", "Technology"]
    titles = [
        "Python Programming",
        "Machine Learning Basics",
        "Healthy Living Tips",
        "Web Development",
    ]

    for i in range(4):
        blog = Blog(
            title=titles[i],
            content=f"Content for blog post {i+1}",
            category=categories[i],
            author_id=test_user.id,
        )
        db_session.add(blog)
        blogs.append(blog)

    db_session.commit()
    for blog in blogs:
        db_session.refresh(blog)
    return blogs
