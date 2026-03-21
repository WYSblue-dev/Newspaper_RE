from django.db import models
from django.conf import settings
from django.urls import reverse


# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=75)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})
