from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from . models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count

def index(request):
    all_group = BloodGroup.objects.annotate(total=Count('donor'))
    return render(request, "index.html", {'all_group':all_group})

def donors_list(request, myid):
    blood_groups = BloodGroup.objects.filter(id=myid).first()
    donor = Donor.objects.filter(blood_group=blood_groups)
    return render(request, "donors_list.html", {'donor':donor})

def donors_details(request, myid):
    details = Donor.objects.filter(id=myid)[0]
    return render(request, "donors_details.html", {'details':details})

def request_blood(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        blood_requests = RequestBlood.objects.create(name=name, email=email, phone=phone, state=state, city=city, address=address, blood_group=BloodGroup.objects.get(name=blood_group), date=date)
        blood_requests.save()
        return render(request, "index.html")
    return render(request, "request_blood.html")

def see_all_request(request):
    requests = RequestBlood.objects.all()
    return render(request, "see_all_request.html", {'requests':requests})

def become_donor(request):
    if request.method=="POST":   
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        gender = request.POST['gender']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        image = request.FILES['image']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')

        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        donors = Donor.objects.create(donor=user, phone=phone, state=state, city=city, address=address, gender=gender, blood_group=BloodGroup.objects.get(name=blood_group), date_of_birth=date, image=image)
        user.save()
        donors.save()
        return render(request, "index.html")
    return render(request, "become_donor.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/profile")
            else:
                thank = True
                return render(request, "user_login.html", {"thank":thank})
    return render(request, "login.html")

def Logout(request):
    logout(request)
    return redirect('/')

@login_required(login_url = '/login')
def profile(request):
    donor_profile = Donor.objects.get(donor=request.user)
    return render(request, "profile.html", {'donor_profile':donor_profile})

@login_required(login_url = '/login')
def edit_profile(request):
    donor_profile = Donor.objects.get(donor=request.user)
    if request.method == "POST":
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']

        donor_profile.donor.email = email
        donor_profile.phone = phone
        donor_profile.state = state
        donor_profile.city = city
        donor_profile.address = address
        donor_profile.save()
        donor_profile.donor.save()

        try:
            image = request.FILES['image']
            donor_profile.image = image
            donor_profile.save()
        except:
            pass
        alert = True
        return render(request, "edit_profile.html", {'alert':alert})
    return render(request, "edit_profile.html", {'donor_profile':donor_profile})

@login_required(login_url = '/login')
def change_status(request):
    donor_profile = Donor.objects.get(donor=request.user)
    if donor_profile.ready_to_donate:
        donor_profile.ready_to_donate = False
        donor_profile.save()
    else:
        donor_profile.ready_to_donate = True
        donor_profile.save()
    return redirect('/profile')