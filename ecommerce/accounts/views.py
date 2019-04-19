from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.http import is_safe_url
from django.views.generic import CreateView, FormView

from . import forms
from accounts.models import GuestEmail
from .signals import user_logged_in

# Create your views here.

class LoginView(FormView):
    form_class = forms.LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'

    def form_valid(self, form):
        next_ = self.request.GET.get('next')
        next_post = self.request.POST.get('next')
        redirect_path = next_ or next_post or None
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(username = email, password = password)
        if user:
            login(self.request, user)
            user_logged_in.send(sender = user.__class__, instance = user, request = self.request)
            try:
                del self.request.session['guest_email_id']
            except:
                pass
            if is_safe_url(redirect_path, self.request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect('/')
        return super(LoginView, self).form_invalid(form)

# def login_page(request):
#     form = forms.LoginForm(request.POST or None)
#     context = {'form': form}
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         user = authenticate(username = username, password = password)
#         if user:
#             login(request, user)
#             try:
#                 del request.session['guest_email_id']
#             except:
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect('/')
#         else:
#             print('Error')
#     return render(request, 'accounts/login.html', context)

class RegisterView(CreateView):
    form_class = forms.RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'

# User = get_user_model()
# def register_page(request):
#     form = forms.RegisterForm(request.POST or None)
#     context = {'form': form}
#     if form.is_valid():
#         form.save()
#         # username = form.cleaned_data.get('username')
#         # email = form.cleaned_data.get('email')
#         # password = form.cleaned_data.get('password')
#         # new_user = User.objects.create_user(username, email, password)
#     return render(request, 'accounts/register.html', context)

def guest_register_view(request):
    form = forms.GuestForm(request.POST or None)
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email = email)
        request.session['guest_email_id'] = new_guest_email.id
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect('/register/')
    return redirect('/register/')