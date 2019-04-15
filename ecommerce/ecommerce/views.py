from django.shortcuts import render

from . import forms


def home_page(request):
    context = {
        'title': 'Home Page',
        'content': 'Welcome to the home page!'
    }
    return render(request, 'home_page.html', context)

def about_page(request):
    context = {
        'title': 'About Page',
        'content': 'Welcome to the about page!'
    }
    return render(request, 'home_page.html', context)

def contacts_page(request):
    form = forms.ContactForm(request.POST or None)
    context = {
        'title': 'Contacts',
        'content': 'Welcome to the contacts page!',
        'form': form
    }
    if form.is_valid():
        print(form.cleaned_data.get('fullname'))
        print(form.cleaned_data.get('email'))
        print(form.cleaned_data.get('content'))
    return render(request, 'contact/view.html', context)

