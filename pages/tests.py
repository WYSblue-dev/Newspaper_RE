from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="homepage_user",
            email="homepage_user@example.com",
            password="Secret!1234",
            age=27,
        )

    @staticmethod
    def grant_permissions(user, *codenames):
        user.user_permissions.add(*Permission.objects.filter(codename__in=codenames))

    def test_home_page_for_anonymous_user_shows_auth_links(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, reverse("login"))
        self.assertContains(response, reverse("signup"))

    def test_home_page_for_authenticated_user_uses_logout_endpoint(self):
        self.client.login(username="homepage_user", password="Secret!1234")

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'action="{reverse("logout")}"')
        self.assertContains(response, "Welcome Back")

    def test_home_page_hides_create_article_link_without_add_article_permission(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "read-only for articles")
        self.assertNotContains(response, reverse("article_new"))

    def test_home_page_shows_create_article_link_with_add_article_permission(self):
        self.grant_permissions(self.user, "add_article")
        self.client.force_login(self.user)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("article_new"))
