from tests.base import BaseTestCase
from parameterized import parameterized
from app.user.models import User
# from app.core.permissions import Permission

class TestUserEndpoints(BaseTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.base_url = "/api/v1/users"
        self.valid_user_data = {
            "username": "newuser@example.com",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User"
        }

    @parameterized.expand([
        ("admin", 200),
        ("member", 403),
    ])
    async def test_create_user_permissions(self, role, expected_status):
        """Test la création d'utilisateur avec différents rôles"""
        user_data = await self.create_user(
            username=f"{role}@test.com",
            password="password",
            role=role
        )

        response = self.client.post(
            self.base_url,
            headers=user_data["headers"],
            json=self.valid_user_data
        )

        self.assertEqual(response.status_code, expected_status)
        if expected_status == 200:
            # Vérifier que l'utilisateur a été créé
            user = await User.get_or_none(username=self.valid_user_data["username"])
            self.assertIsNotNone(user)
            await user.delete()

    async def test_create_user_duplicate_email(self):
        """Test la création d'un utilisateur avec un email qui existe déjà"""
        # Créer le premier utilisateur
        response = self.client.post(
            self.base_url,
            headers=self.admin_data["headers"],
            json=self.valid_user_data
        )
        self.assertEqual(response.status_code, 200)

        # Essayer de créer un deuxième utilisateur avec le même email
        response = self.client.post(
            self.base_url,
            headers=self.admin_data["headers"],
            json=self.valid_user_data
        )
        self.assertEqual(response.status_code, 400)

    @parameterized.expand([
        ("admin", True),
        ("member", False),
    ])
    async def test_list_users(self, role, can_access):
        """Test la liste des utilisateurs avec différents rôles"""
        user_data = await self.create_user(
            username=f"{role}@test.com",
            password="password",
            role=role
        )

        response = self.client.get(
            self.base_url,
            headers=user_data["headers"]
        )

        expected_status = 200 if can_access else 403
        self.assertEqual(response.status_code, expected_status)

        if can_access:
            data = response.json()
            self.assertIsInstance(data, list)

    async def test_update_user_profile(self):
        """Test la mise à jour du profil utilisateur"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }

        response = self.client.put(
            f"{self.base_url}/me",
            headers=self.user_data["headers"],
            json=update_data
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Updated")
        self.assertEqual(data["last_name"], "Name")

        # Vérifier en base de données
        user = await User.get(id=self.user_data["user"].id)
        self.assertEqual(user.first_name, "Updated")

    async def test_change_password(self):
        """Test le changement de mot de passe"""
        password_data = {
            "current_password": "userpass",
            "new_password": "newpassword123"
        }

        response = self.client.post(
            f"{self.base_url}/me/change-password",
            headers=self.user_data["headers"],
            json=password_data
        )

        self.assertEqual(response.status_code, 200)

        # Vérifier que le nouveau mot de passe fonctionne
        login_response = self.client.post(
            "/api/v1/token",
            data={
                "username": self.user_data["user"].username,
                "password": "newpassword123"
            }
        )
        self.assertEqual(login_response.status_code, 200)

    @parameterized.expand([
        #("admin", Permission.USER_DELETE, 204),
        ("member", None, 403),
    ])
    async def test_delete_user(self, role, permission, expected_status):
        """Test la suppression d'utilisateur avec différents rôles"""
        # Créer un utilisateur à supprimer
        test_user = await self.create_user(
            username="todelete@example.com",
            password="deletepass"
        )

        # Créer l'utilisateur qui va faire la suppression
        user_data = await self.create_user(
            username=f"{role}@test.com",
            password="password",
            role=role
        )

        if permission:
            user_data["user"].custom_permissions = [permission]
            await user_data["user"].save()

        response = self.client.delete(
            f"{self.base_url}/{test_user['user'].id}",
            headers=user_data["headers"]
        )

        self.assertEqual(response.status_code, expected_status)

        if expected_status == 204:
            # Vérifier que l'utilisateur a été supprimé
            user = await User.get_or_none(id=test_user["user"].id)
            self.assertIsNone(user)
