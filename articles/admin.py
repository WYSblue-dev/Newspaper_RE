from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from .models import Article, Comment


class CommentInline(TabularInline):
    model = Comment
    extra = 0


# Register your models here.
class ArticleAdmin(ModelAdmin):
    inlines = [CommentInline]
    model = Article
    list_display = [
        "title",
        "author",
        "date_added",
    ]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
