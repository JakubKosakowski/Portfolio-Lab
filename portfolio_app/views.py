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
        donated_categories = Category.objects.filter(id__in=request.POST.getlist("categories"))
        donated_institution = Institution.objects.get(id=request.POST.get("organization"))
        donation = Donation.objects.create(quantity=request.POST.get("bags"),
                                           institution=donated_institution,
                                           address=request.POST.get("address"),
                                           phone_number=request.POST.get("phone"),
                                           city=request.POST.get("city"),
                                           zip_code=request.POST.get("postcode"),
                                           pick_up_date=request.POST.get("data"),
                                           pick_up_time=request.POST.get("time"),
                                           pick_up_comment=request.POST.get("more_info"),
                                           user=request.user)
        donation.categories.set(donated_categories)
        donation.save()
        return render(request, "form-confirmation.html")


class UserProfileView(View):
    def get(self, request):
        donations = Donation.objects.filter(user=request.user).order_by('is_taken')
        return render(request, 'profile.html', {'donations': donations})

    def post(self, request):
        donation = Donation.objects.get(id=request.POST.get("donation"))
        donation.is_taken = not donation.is_taken
        donation.save()
        return redirect('profile')


class EditProfileView(View):
    def get(self,request):
        return render(request, 'edit.html')

    def post(self, request):
        if request.POST.get("type") == "edit_data":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email_address = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email_address
                request.user.save()
                return redirect('profile')
            else:
                return render(request, 'edit.html', {"message": "Podane hasło jest nieprawidłowe!"})
        else:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            repeat_new_password = request.POST.get('repeat_new_password')
            user = authenticate(username=request.user.username, password=old_password)
            if user is not None:
                if new_password != repeat_new_password:
                    return render(request, 'edit.html', {"message": "Nowe hasła nie są takie same!"})
                request.user.set_password(new_password)
                request.user.save()
                return redirect('landing_page')
            else:
                return render(request, 'edit.html', {"message": "Stare hasło jest nieprawidłowe!"})

