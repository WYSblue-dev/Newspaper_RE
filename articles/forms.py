from django.forms import ModelForm
from .models import Article
from django import forms


class CustomArticleCreationForm(ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "body",
        ]
        labels = {"title": "Title", "body": "Your thoughts ideas... feelings...."}
        help_text = {}


class CustomArticleUpdateViewForm(ModelForm):
    class Meta:
        model = Article
        fields = ["body"]
        labels = {"body": ""}
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "cols": 20,
                    "rows": 2,
                }
            )
        }
