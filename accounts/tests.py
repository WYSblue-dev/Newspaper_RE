from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserManagersTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_user_creation(self):
        test_user = self.user_model.objects.create_user(
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
        test_super_user = self.user_model.objects.create_superuser(
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

    def test_superuser_creation_rejects_non_staff_flag(self):
        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True."):
            self.user_model.objects.create_superuser(
                username="broken_superuser",
                email="broken_superuser@example.com",
                password="test_super_user_pass",
                age=30,
                is_staff=False,
            )


class TestSignUpView(TestCase):
    def test_signup_exists_at_exact_location(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_by_name(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name="registration/signup.html")
        self.assertContains(response, "Create an account")

    def test_signup_view(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "signup_test",
                "email": "signup_test@example.com",
                "password1": "Secret!12herryscary",
                "password2": "Secret!12herryscary",
                "age": 21,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(get_user_model().objects.first().username, "signup_test")
        self.assertEqual(
            get_user_model().objects.first().email,
            "signup_test@example.com",
        )

    def test_signup_with_password_mismatch_does_not_create_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "signup_test",
                "email": "signup_test@example.com",
                "password1": "Secret!12herryscary",
                "password2": "Secret!12different",
                "age": 21,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertContains(response, "The two password fields didn")

    def test_signup_without_age_does_not_create_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "signup_test",
                "email": "signup_test@example.com",
                "password1": "Secret!12herryscary",
                "password2": "Secret!12herryscary",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertFormError(response.context["form"], "age", "This field is required.")
