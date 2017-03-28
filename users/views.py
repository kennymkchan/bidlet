from django.contrib.auth import (
    get_user_model,
    authenticate,
    login,
    logout,
)
from rest_framework.response import Response
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from functools import reduce
from .forms import (
    AccountLoginForm,
    AccountRegistrationForm,
    UserRegistrationForm,
    AccountEditForm,
    PaymentForm
)
from api.forms import SearchPropertyForm
from api.models import Bidders, Property
from users.models import Account
from django.conf import settings
import stripe

@login_required(login_url="/login/")
def home_view(request):

    user = request.user

    current_bids = Bidders.objects.filter(userID=user.id)
    user_properties = []

    # Note, query sets of cache, so subsequent for loop calls will only execute once
    for bid in current_bids:
        user_properties.append(bid.biddingID)

    # Creates a list of unique propertyID (since a user can have multiple bids on the same prop)
    user_properties = list(set(user_properties))

    # Query a set of properties that the user is watching
    # DO NOT exclude the inactive ones, because they provide useful information as well
    property_queryset = Property.objects.filter(propertyID__in=user_properties)
    # Might want to do a exlude(status="inactive" and user.id !== self.userID)

    # accounts hold most of the properties
    account_queryset = Account.objects.get(user_id = user.id)
    context = {
        "account": account_queryset,
        "properties": property_queryset,
    }

    return render(request, 'accounts/home.html', context)

@login_required(login_url="/login/")
def profile_edit_view(request):
    user = request.user
    # should only have one match but just for precaution
    account_queryset = Account.objects.filter(user_id = user.id).first()

    # Without None, it will always be initialized with a post (tries to post to db)
    accountEditForm = AccountEditForm(request.POST or None, request.FILES or None, instance=account_queryset)
    if accountEditForm.is_valid():
        account = accountEditForm.save(commit=False)
        # In case altering the data is needed.
        account.save()

        # Reset the form to remove all the errors
        accountEditForm = AccountEditForm(request.POST or None, request.FILES or None)
        messages.success(request, 'Profile Information Updated!')
        return redirect('/user/edit')

    context = {
        "accountEditForm": accountEditForm,
        "title": "edit",
        "account": account_queryset,
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required(login_url="/login/")
def payments_view(request):
    user = request.user

    account_queryset = Account.objects.get(user_id=user.id)

    # Might want to try to add an instance to this, so previous cc info shows
    # Need to store partially hidden cc info
    paymentForm = PaymentForm(request.POST or None)

    if paymentForm.is_valid():

        card_number = paymentForm.cleaned_data.get("number")
        card_cv = paymentForm.cleaned_data.get("cv")
        card_exp_month = paymentForm.cleaned_data.get("exp_month")
        card_exp_year = paymentForm.cleaned_data.get("exp_year")

        stripe.api_key = settings.STRIPE_KEY

        # Checks if the token is valid
        try:
            token = stripe.Token.create(
                card={
                    "number": card_number,
                    "exp_month": card_exp_month,
                    "exp_year": card_exp_year,
                    "cvc": card_cv,
                },
            )

        # If the token is not valid, return an error to the page
        except:
            messages.error(request, 'Credit card information is invalid!')
            return redirect('/user/payments')

        # Create a customer on stripe
        stripe_customer = stripe.Customer.create(
            card = token,
            description = user
        )

        # Update account with the right stripe id
        Account.objects.select_for_update().filter(user_id=user.id).update(stripe_id=stripe_customer.id)

        messages.success(request, 'Credit card information has been added!')
        return redirect('/user/payments')

    context = {
        "paymentForm": paymentForm,
        "title": "payment_method",
        "account": account_queryset,
    }

    return render(request, 'accounts/payments.html', context)

def login_view(request):
    # get next page for login required
    next_page = request.GET.get("next")
    title = "Login"

    # If already logged in, go to home page
    user = request.user
    if user.is_authenticated():
        return redirect('/home')

    loginForm = AccountLoginForm(request.POST or None)
    if loginForm.is_valid():
        username = loginForm.cleaned_data.get("username")
        password = loginForm.cleaned_data.get("password")
        user = authenticate(username=username, password=password) # auth user
        login(request, user) # base login template from django

        # Check if they are trying to access a page that requires login, else,
        # just redirect them to home
        if next_page:
            return redirect(next_page)
        else:
            return redirect('/home')

    return render(request, 'accounts/login.html', {"form": loginForm, "title": title})

def registration_view(request):

    # If already logged in, go to home page
    user = request.user
    if user.is_authenticated():
        return redirect('/home')

    # get next page for login required
    next_page = request.GET.get("next")

    title = "Register"

    userRegisterForm = UserRegistrationForm(request.POST or None)
    accountRegisterForm = AccountRegistrationForm(request.POST or None)
    if userRegisterForm.is_valid() and accountRegisterForm.is_valid():
        user = userRegisterForm.save(commit=False)
        account = accountRegisterForm.save(commit=False)

        username = userRegisterForm.cleaned_data.get("username")
        password = userRegisterForm.cleaned_data.get("password")
        email = userRegisterForm.cleaned_data.get("email")
        first_name = userRegisterForm.cleaned_data.get("first_name")
        user.set_password(password)
        user.save()
        newUser = authenticate(username=username, password=password) # auth user
        account.user_id = newUser.id
        account.save()
        login(request, newUser)

        try:
            sendMail(email, first_name)
        except:
            print("Email send failed - Connection Error")

        # Check if they are trying to access a page that requires login, else,
        # just redirect them to home
        if next_page:
            return redirect(next_page)
        else:
            return redirect('/home')

    context = {
        "user_form": userRegisterForm,
        "account_form": accountRegisterForm,
        "title": title,
    }

    return render(request, 'accounts/register.html', context)

def sendMail(email, first):

    fields = {
        'email': email,
        'first_name': first
    }

    message_plain = render_to_string('email/signup-email.txt', fields)
    message_html = render_to_string('email/signup-email.html', fields)
    subject_title = "Bidlet - One step closer to a new home"

    send_mail(
        subject_title,
        message_plain,
        settings.EMAIL_HOST_USER,
        # replce with email from params
        ['kennykitchan@gmail.com'],
        # Allows us to send HTML template emails
        html_message=message_html,
    )

def logout_view(request):
    logout(request)
    return redirect('/')
