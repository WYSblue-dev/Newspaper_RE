from django.forms import ModelForm
from .models import Article


class CustomArticleCreationForm(ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "body",
        ]
        labels = {"title": "Title", "body": "Your thoughts ideas... feelings...."}
        help_text = {}
