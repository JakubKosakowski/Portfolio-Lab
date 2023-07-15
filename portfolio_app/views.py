from django.shortcuts import render, redirect
from django.http import request, HttpResponse
from django.views import View
from .models import *


# Create your views here.
class LandingPageView(View):
    def get(self, request):
        received_sacks = 0
        supported_institutions = 0
        for donation in Donation.objects.all():
            received_sacks += donation.quantity
        for institution in Institution.objects.all():
            supported_institutions += 1 if len(institution.donation_set.all()) > 0 else 0
        return render(request, 'index.html',
                      {'received_sacks': received_sacks, 'supported_institutions': supported_institutions})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')


class AddDonationView(View):
    def get(self, request):
        return render(request, 'form.html')
