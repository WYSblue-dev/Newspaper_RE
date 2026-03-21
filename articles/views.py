from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Article, Comment
from .forms import (
    CustomArticleCreationForm,
    CustomArticleUpdateViewForm,
    CustomCommentForm,
)


class StrictPermissionRequiredMixin(PermissionRequiredMixin):
    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path())
        return super().handle_no_permission()


class AuthorRequiredMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.get_object().author_id == self.request.user.id

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path())
        return super().handle_no_permission()


class ArticleDetailView(DetailView):
    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["form"] = kwargs.get("form") or CustomCommentForm()
        context["comments"] = self.object.comment_set.select_related("author").order_by(
            "-date_added"
        )
        context["can_add_comment"] = user.is_authenticated and user.has_perm(
            "articles.add_comment"
        )
        context["can_change_article"] = (
            user.is_authenticated
            and self.object.author_id == user.id
            and user.has_perm("articles.change_article")
        )
        context["can_delete_article"] = (
            user.is_authenticated
            and self.object.author_id == user.id
            and user.has_perm("articles.delete_article")
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm("articles.add_comment"):
            raise PermissionDenied

        form = CustomCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = self.object
            comment.author = request.user
            comment.save()
            return HttpResponseRedirect(self.object.get_absolute_url())

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ArticleListView(ListView):
    model = Article
    template_name = "article_list.html"
    context_object_name = "articles"


class ArticleCreateView(LoginRequiredMixin, StrictPermissionRequiredMixin, CreateView):
    model = Article
    form_class = CustomArticleCreationForm
    template_name = "article_new.html"
    permission_required = "articles.add_article"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleUpdateView(
    LoginRequiredMixin,
    StrictPermissionRequiredMixin,
    AuthorRequiredMixin,
    UpdateView,
):
    model = Article
    template_name = "article_update.html"
    form_class = CustomArticleUpdateViewForm
    permission_required = "articles.change_article"


class ArticleDeleteView(
    LoginRequiredMixin,
    StrictPermissionRequiredMixin,
    AuthorRequiredMixin,
    DeleteView,
):
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")
    permission_required = "articles.delete_article"


class CommentUpdateView(
    LoginRequiredMixin,
    StrictPermissionRequiredMixin,
    AuthorRequiredMixin,
    UpdateView,
):
    template_name = "comment_update.html"
    model = Comment
    form_class = CustomCommentForm
    permission_required = "articles.change_comment"


class CommentDeleteView(
    LoginRequiredMixin,
    StrictPermissionRequiredMixin,
    AuthorRequiredMixin,
    DeleteView,
):
    template_name = "comment_delete.html"
    model = Comment
    permission_required = "articles.delete_comment"

    def get_success_url(self):
        return self.object.article.get_absolute_url()
