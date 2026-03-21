from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import Article, Comment


class PermissionHelperMixin:
    @staticmethod
    def grant_permissions(user, *codenames):
        permissions = {
            perm.codename: perm
            for perm in Permission.objects.filter(codename__in=codenames)
        }
        missing_permissions = set(codenames) - permissions.keys()
        if missing_permissions:
            raise ValueError(
                f"Missing permissions in test setup: {sorted(missing_permissions)}"
            )
        user.user_permissions.add(*permissions.values())


class ArticleModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="author",
            email="author@example.com",
            password="Secret!1234",
            age=33,
        )
        cls.article = Article.objects.create(
            title="test article",
            body="This is the body for the article.",
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            comment="This comment is definitely longer than fourteen characters.",
            article=cls.article,
            author=cls.user,
        )

    def test_article_get_absolute_url(self):
        self.assertEqual(
            self.article.get_absolute_url(),
            reverse("article_detail", kwargs={"pk": self.article.pk}),
        )

    def test_comment_string_representation_is_truncated(self):
        self.assertEqual(str(self.comment), "This comment i")

    def test_comment_absolute_url_routes_back_to_article(self):
        self.assertEqual(
            self.comment.get_absolute_url(),
            reverse("article_detail", kwargs={"pk": self.article.pk}),
        )


class ArticleListViewEdgeCaseTests(TestCase):
    def test_article_list_displays_empty_state_when_no_articles_exist(self):
        response = self.client.get(reverse("article_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No articles have been created yet.")


class ArticleAuthorizationTests(PermissionHelperMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="author",
            email="author@example.com",
            password="Secret!1234",
            age=33,
        )
        cls.reader = get_user_model().objects.create_user(
            username="reader",
            email="reader@example.com",
            password="Secret!4321",
            age=29,
        )
        cls.article = Article.objects.create(
            title="first article",
            body="Original article body.",
            author=cls.author,
        )
        cls.comment = Comment.objects.create(
            comment="Original comment body.",
            article=cls.article,
            author=cls.author,
        )

    def test_anonymous_user_is_redirected_from_article_create(self):
        response = self.client.get(reverse("article_new"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('article_new')}",
        )

    def test_logged_in_user_without_add_article_permission_gets_forbidden(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("article_new"),
            {
                "title": "second article",
                "body": "Body for a second article.",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Article.objects.filter(title="second article").exists())

    def test_authenticated_article_create_requires_add_article_permission(self):
        self.grant_permissions(self.author, "add_article")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("article_new"),
            {
                "title": "second article",
                "body": "Body for a second article.",
            },
        )

        created_article = Article.objects.get(title="second article")
        self.assertRedirects(
            response,
            reverse("article_detail", kwargs={"pk": created_article.pk}),
        )
        self.assertEqual(created_article.author, self.author)

    def test_owner_without_change_article_permission_cannot_update(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("article_update", kwargs={"pk": self.article.pk}),
            {"body": "Owner update attempt without permission."},
        )

        self.article.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.article.body, "Original article body.")

    def test_non_author_with_change_article_permission_cannot_update(self):
        self.grant_permissions(self.reader, "change_article")
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse("article_update", kwargs={"pk": self.article.pk}),
            {"body": "A malicious update attempt."},
        )

        self.article.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.article.body, "Original article body.")

    def test_owner_with_change_article_permission_can_update(self):
        self.grant_permissions(self.author, "change_article")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("article_update", kwargs={"pk": self.article.pk}),
            {"body": "Updated article body by the owner."},
        )

        self.article.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("article_detail", kwargs={"pk": self.article.pk}),
        )
        self.assertEqual(self.article.body, "Updated article body by the owner.")

    def test_owner_without_delete_article_permission_cannot_delete(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("article_delete", kwargs={"pk": self.article.pk})
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Article.objects.filter(pk=self.article.pk).exists())

    def test_non_author_with_delete_article_permission_cannot_delete(self):
        self.grant_permissions(self.reader, "delete_article")
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse("article_delete", kwargs={"pk": self.article.pk})
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Article.objects.filter(pk=self.article.pk).exists())

    def test_owner_with_delete_article_permission_can_delete(self):
        self.grant_permissions(self.author, "delete_article")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("article_delete", kwargs={"pk": self.article.pk})
        )

        self.assertRedirects(response, reverse("article_list"))
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())

    def test_anonymous_comment_submission_redirects_to_login(self):
        response = self.client.post(
            reverse("article_detail", kwargs={"pk": self.article.pk}),
            {"comment": "A drive-by comment."},
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('article_detail', kwargs={'pk': self.article.pk})}",
        )
        self.assertEqual(Comment.objects.count(), 1)

    def test_logged_in_user_without_add_comment_permission_gets_forbidden(self):
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse("article_detail", kwargs={"pk": self.article.pk}),
            {"comment": "This should not be accepted."},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 1)

    def test_blank_comment_is_rejected_for_authorized_user(self):
        self.grant_permissions(self.author, "add_comment")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("article_detail", kwargs={"pk": self.article.pk}),
            {"comment": "   "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertFormError(
            response.context["form"], "comment", "This field is required."
        )

    def test_valid_comment_is_created_only_with_add_comment_permission(self):
        self.grant_permissions(self.reader, "add_comment")
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse("article_detail", kwargs={"pk": self.article.pk}),
            {"comment": "This article needed a comment."},
        )

        self.assertRedirects(
            response,
            reverse("article_detail", kwargs={"pk": self.article.pk}),
        )
        self.assertEqual(Comment.objects.count(), 2)
        created_comment = Comment.objects.exclude(pk=self.comment.pk).get()
        self.assertEqual(created_comment.author, self.reader)
        self.assertEqual(created_comment.article, self.article)

    def test_anonymous_user_is_redirected_from_comment_update(self):
        response = self.client.get(
            reverse("comment_update", kwargs={"pk": self.comment.pk})
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('comment_update', kwargs={'pk': self.comment.pk})}",
        )

    def test_owner_without_change_comment_permission_cannot_update_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("comment_update", kwargs={"pk": self.comment.pk}),
            {"comment": "Edited without permission."},
        )

        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.comment.comment, "Original comment body.")

    def test_non_author_with_change_comment_permission_cannot_update_comment(self):
        self.grant_permissions(self.reader, "change_comment")
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse("comment_update", kwargs={"pk": self.comment.pk}),
            {"comment": "Edited by non-owner."},
        )

        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.comment.comment, "Original comment body.")

    def test_owner_with_change_comment_permission_can_update_comment(self):
        self.grant_permissions(self.author, "change_comment")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("comment_update", kwargs={"pk": self.comment.pk}),
            {"comment": "Updated comment body."},
        )

        self.comment.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("article_detail", kwargs={"pk": self.article.pk}),
        )
        self.assertEqual(self.comment.comment, "Updated comment body.")

    def test_owner_without_delete_comment_permission_cannot_delete_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("comment_delete", kwargs={"pk": self.comment.pk})
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_non_author_with_delete_comment_permission_cannot_delete_comment(self):
        self.grant_permissions(self.reader, "delete_comment")
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse("comment_delete", kwargs={"pk": self.comment.pk})
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_owner_with_delete_comment_permission_can_delete_comment(self):
        self.grant_permissions(self.author, "delete_comment")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("comment_delete", kwargs={"pk": self.comment.pk})
        )

        self.assertRedirects(
            response,
            reverse("article_detail", kwargs={"pk": self.article.pk}),
        )
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


class ArticleTemplateAuthorizationTests(PermissionHelperMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="author",
            email="author@example.com",
            password="Secret!1234",
            age=33,
        )
        cls.reader = get_user_model().objects.create_user(
            username="reader",
            email="reader@example.com",
            password="Secret!4321",
            age=29,
        )
        cls.article = Article.objects.create(
            title="first article",
            body="Original article body.",
            author=cls.author,
        )
        cls.comment = Comment.objects.create(
            comment="Original comment body.",
            article=cls.article,
            author=cls.author,
        )

    def test_detail_view_hides_comment_form_when_user_lacks_add_comment_permission(
        self,
    ):
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("article_detail", kwargs={"pk": self.article.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "does not have permission to add comments",
        )
        self.assertNotContains(response, 'name="comment"')

    def test_detail_view_shows_comment_form_when_user_has_add_comment_permission(self):
        self.grant_permissions(self.reader, "add_comment")
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("article_detail", kwargs={"pk": self.article.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="comment"')

    def test_detail_view_hides_article_controls_when_owner_lacks_permissions(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("article_detail", kwargs={"pk": self.article.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse("article_update", kwargs={"pk": self.article.pk}),
        )
        self.assertNotContains(
            response,
            reverse("article_delete", kwargs={"pk": self.article.pk}),
        )

    def test_detail_view_shows_article_controls_only_for_owner_with_permissions(self):
        self.grant_permissions(self.author, "change_article", "delete_article")
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("article_detail", kwargs={"pk": self.article.pk})
        )

        self.assertContains(
            response,
            reverse("article_update", kwargs={"pk": self.article.pk}),
        )
        self.assertContains(
            response,
            reverse("article_delete", kwargs={"pk": self.article.pk}),
        )

    def test_detail_view_shows_comment_controls_only_for_owner_with_permissions(self):
        self.grant_permissions(self.author, "change_comment", "delete_comment")
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("article_detail", kwargs={"pk": self.article.pk})
        )

        self.assertContains(
            response,
            reverse("comment_update", kwargs={"pk": self.comment.pk}),
        )
        self.assertContains(
            response,
            reverse("comment_delete", kwargs={"pk": self.comment.pk}),
        )

    def test_detail_view_hides_comment_controls_for_non_owner_even_with_permissions(
        self,
    ):
        self.grant_permissions(self.reader, "change_comment", "delete_comment")
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("article_detail", kwargs={"pk": self.article.pk})
        )

        self.assertNotContains(
            response,
            reverse("comment_update", kwargs={"pk": self.comment.pk}),
        )
        self.assertNotContains(
            response,
            reverse("comment_delete", kwargs={"pk": self.comment.pk}),
        )
