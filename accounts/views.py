from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import CustomUser
from .forms import CustomUserCreationForm


# Create your views here.
class SignUpView(CreateView):
    # this is redundent but I like the rigidity for creation.
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    # needed for initilization
    success_url = reverse_lazy("login")
