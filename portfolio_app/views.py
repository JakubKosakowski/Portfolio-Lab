from django.shortcuts import render, redirect
from django.http import request, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .models import *


# Create your views here.
class LandingPageView(View):
    def get(self, request):
        received_sacks = 0
        supported_institutions = 0
        all_organizations = {0: [], 1: [], 2: []}
        for donation in Donation.objects.all():
            received_sacks += donation.quantity
        for institution in Institution.objects.all():
            supported_institutions += 1 if len(institution.donation_set.all()) > 0 else 0
            all_organizations[institution.types].append(institution)
        return render(request, 'index.html',
                      {'received_sacks': received_sacks, 'supported_institutions': supported_institutions,
                       'foundations': all_organizations[0],
                       'non_gov_organizations': all_organizations[1],
                       'local_collections': all_organizations[2]})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        try:
            user = User.objects.get(username=request.POST.get("email"))
            user = authenticate(username=request.POST.get("email"), password=request.POST.get("password"))
            if user is not None:
                login(request, user)
                return redirect('landing_page')
            else:
                return render(request, 'login.html', {"messages": ["Zły login lub hasło"]})
        except User.DoesNotExist:
            return redirect('register')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        messages = []
        if any(c.isdigit() for c in request.POST.get("name")):
            messages.append("Imię nie powinno zawierać liczb!")
        if any(c.isdigit() for c in request.POST.get("surname")):
            messages.append("Nazwisko nie powinno zawierać liczb!")
        if request.POST.get("password") != request.POST.get("password2"):
            messages.append("Hasła nie są takie same!")
        if User.objects.get(email=request.POST.get("email")):
            messages.append("Konto z takim adresem mailowym już istnieje!")
        if len(messages) > 0:
            return render(request, 'register.html', {"messages": messages})
        else:
            User.objects.create_user(username=request.POST.get("email"),
                                     email=request.POST.get("email"),
                                     password=request.POST.get("password"),
                                     first_name=request.POST.get('name'),
                                     last_name=request.POST.get('surname'))
            return redirect('login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('landing_page')


class AddDonationView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'form.html', {'categories': Category.objects.all(),
                                                 'institutions': Institution.objects.all()})
        return redirect('login')

    def post(self, request):
        donated_categories = request.POST.getlist("categories")
        donated_institution = Institution.objects.get(id=request.POST.get("organization"))
        donation = Donation.objects.create(quantity=request.POST.get("bags"),
                                           address=request.POST.get("address"),
                                           phone_number=request.POST.get("phone"),
                                           city=request.POST.get("city"),
                                           zip_code=request.POST.get("postcode"),
                                           pick_up_date=request.POST.get("data"),
                                           pick_up_time=request.POST.get("time"),
                                           pick_up_comment=request.POST.get("more_info"))
        donation.categories.add(donated_categories)
        donation.institution.add(donated_institution)
        donation.save()
        return render(request, "form-confirmation.html")
