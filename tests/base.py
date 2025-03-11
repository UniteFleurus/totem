from tortoise.contrib.test import TestCase
from app.user.models import User
from app.core.security import create_access_token, get_password_hash
from fastapi.testclient import TestClient
from app.main import app


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = TestClient(app)
        self.db_url = "sqlite://:memory:"
        self.modules = {"models": ["app.user.models"]}

    async def create_user(self, username="test@example.com", password="testpassword", role="member"):
        """Helper pour créer un utilisateur de test"""
        user = await User.create(
            username=username,
            email=username,
            hashed_password=get_password_hash(password),
            role=role
        )
        token = create_access_token(data={"sub": user.username})
        return {
            "user": user,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"}
        }

    async def asyncSetUp(self):
        await super().asyncSetUp()
        # Créer un utilisateur admin et un utilisateur normal pour les tests
        self.admin_data = await self.create_user(
            username="admin@example.com",
            password="adminpass",
            role="admin"
        )
        self.user_data = await self.create_user(
            username="user@example.com",
            password="userpass",
            role="member"
        )
