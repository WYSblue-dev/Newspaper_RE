from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        fields = UserCreationForm.Meta.fields + ("age",)


class CustomUserChangeForm(UserCreationForm):
    class Meta:
        fields = UserCreationForm.Meta.fields
