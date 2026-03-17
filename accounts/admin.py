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

    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {"fields": ("age",)},
        ),
    )
    # due to the newer usable password of django we can't use the old feilds
    # we must define ourselves. Due to django trying to say a password exist
    # even though we're trying to create.
    add_fieldsets = (
        (
            None,
            {
                # must add password fields here for us to enter for the account
                # we create
                "fields": (
                    "username",
                    "email",
                    "age",
                    "password1",
                    "password2",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
