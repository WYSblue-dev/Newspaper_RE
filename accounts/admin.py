from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = [
        "username",
        "age",
        "email",
    ]

    fieldsets = UserAdmin.fieldsets + ("age",)
    add_fieldsets = UserAdmin.add_fieldsets + ("age",)


admin.site.register(CustomUser, CustomUserAdmin)
