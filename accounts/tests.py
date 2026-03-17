from django.test import TestCase
from django.contrib.auth import get_user_model

# Create your tests here.


# use TestCase here since users are tied to the db
class UserManagersTests(TestCase):

    def test_user_creation(self):
        User = get_user_model()
        test_user = User.objects.create_user(
            username="test_user",
            email="test_user@example.com",
            password="secret",
            age=30,
        )

        self.assertEqual(test_user.username, "test_user")
        self.assertEqual(test_user.email, "test_user@example.com")
        self.assertEqual(int(test_user.age), 30)
        self.assertTrue(test_user.is_active)
        self.assertFalse(test_user.is_superuser)
        self.assertFalse(test_user.is_staff)

    def test_superuser_creation(self):
        User = get_user_model()
        test_super_user = User.objects.create_superuser(
            username="test_super_user",
            email="test_super_user@example.com",
            password="test_super_user_pass",
            age=30,
        )
        self.assertEqual(test_super_user.username, "test_super_user")
        self.assertEqual(test_super_user.email, "test_super_user@example.com")
        self.assertTrue(test_super_user.is_authenticated)
        self.assertTrue(test_super_user.is_staff)
        self.assertTrue(test_super_user.is_active)
        self.assertTrue(test_super_user.is_superuser)
