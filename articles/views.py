from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Article


# Create your views here.
class ArticleDetailView(DetailView):
    model = Article
    template_name = "article_detail.html"


class ArticleListView(ListView):
    model = Article
    template_name = "article_list.html"
    context_object_name = "articles"


class ArticleCreateView(CreateView):
    model = Article
    fields = [
        "title",
        "body",
    ]
    template_name = "article_new.html"

    # I believe this works as I intend it to.
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        form.save()
        return super().form_valid(form)


class ArticleUpdateView(UpdateView):
    model = Article
    template_name = "article_update.html"

    fields = ["body"]


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = "article_delete.html"

    # we could change this out for a notification page if we wanted.
    success_url = reverse_lazy("article_list.html")
