from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

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

    # assuming that this means changes work for now.
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


class TestSignUpView(TestCase):
    def test_signup_exist_at_exact_location(self):
        # accounts signup page
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_by_name(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name="registration/signup.html")
        self.assertContains(response, "Sign Up")

    def test_signup_view(self):
        response = self.client.post(
            reverse(
                "signup",
            ),
            # take note that this data passed is not as kwargs just as data in
            # the shape of of kwargs for the context more than likly.
            {
                "username": "signup_test",
                # email isn't working must apply to the creation form
                "email": "signup_test@example.com",
                "password1": "Secret!12herryscary",
                "password2": "Secret!12herryscary",
                "age": 21,
            },
        )
        # should be a redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].username, "signup_test")
        self.assertEqual(
            # uses the class CustomUser model and queries it for all objs with
            # indexing then attribute access to test against the value.
            get_user_model().objects.all()[0].email,
            "signup_test@example.com",
        )
