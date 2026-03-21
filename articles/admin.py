from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Article


# Register your models here.
class ArticleAdmin(ModelAdmin):
    model = Article
    list_display = [
        "title",
        "author",
        "date_added",
    ]


admin.site.register(Article, ArticleAdmin)
