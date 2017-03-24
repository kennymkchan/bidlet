from django.contrib.auth import (
    get_user_model,
    authenticate,
    login,
    logout,
)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import (AccountLoginForm, AccountRegistrationForm, UserRegistrationForm, AccountEditForm)
from users.models import Account

@login_required(login_url="/login/")
def home_view(request):

    user = request.user

    # should only have one match but just for precaution
    # accounts hold most of the properties
    account_queryset = Account.objects.filter(user_id = user.id).first()
    context = {
        "account": account_queryset,
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
        return redirect('/user/edit')

    context = {
        "accountEditForm": accountEditForm,
        "title": "edit",
        "account": account_queryset,
    }
    return render(request, 'accounts/profile_edit.html', context)

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
        user.set_password(password)
        user.save()
        newUser = authenticate(username=username, password=password) # auth user
        account.user_id = newUser.id
        account.save()
        login(request, newUser)

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

def logout_view(request):
    logout(request)
    return redirect('/')
