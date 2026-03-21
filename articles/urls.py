from django.urls import path
from .views import (
    ArticleDetailView,
    ArticleListView,
    ArticleCreateView,
    ArticleUpdateView,
    ArticleDeleteView,
    CommentUpdateView,
    CommentDeleteView,
)

urlpatterns = [
    path(
        "article_detail/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"
    ),
    path("article_list/", ArticleListView.as_view(), name="article_list"),
    path("article_new/", ArticleCreateView.as_view(), name="article_new"),
    path(
        "article_update/<int:pk>/", ArticleUpdateView.as_view(), name="article_update"
    ),
    path(
        "article_delete/<int:pk>/", ArticleDeleteView.as_view(), name="article_delete"
    ),
    path(
        "comment_update/<int:pk>/", CommentUpdateView.as_view(), name="comment_update"
    ),
    path(
        "comment_delete/<int:pk>/", CommentDeleteView.as_view(), name="comment_delete"
    ),
]
