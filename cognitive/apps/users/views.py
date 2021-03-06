import urllib
import json

from functools import wraps

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import IntegrityError
from django.http.response import (HttpResponseRedirect, JsonResponse)
from django.shortcuts import (render, get_object_or_404,
                              redirect)

from rest_framework import status
from rest_framework.authtoken.models import Token

from cognitive import settings
from cognitive.apps.users.models import User
from .forms import UserEditForm, UserCreateForm


def to_json_response(response):
    status_code = response.status_code
    data = None

    if status.is_success(status_code):
        if hasattr(response, 'is_rendered') and not response.is_rendered:
            response.render()
        data = {'data': response.content}

    elif status.is_redirect(status_code):
        data = {'redirect': response.url}

    elif (status.is_client_error(status_code) or
          status.is_server_error(status_code)):
        data = {'errors': [{
            'status': status_code
        }]}

    return JsonResponse(data)


def accepts_ajax(ajax_template_name=None):
    """
    Decorator for views that checks if the request was made
    via an XMLHttpRequest. Calls the view function and
    converts the output to JsonResponse.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.is_ajax():
                kwargs['template_name'] = ajax_template_name
                response = view_func(request, *args, **kwargs)
                return to_json_response(response)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@accepts_ajax(ajax_template_name='registration/_signup.html')
def create_user(request, template_name='registration/signup.html'):
    if request.method == "POST":
        form = UserCreateForm(request.POST, request.FILES, instance=User())
        if form.is_valid():
            if settings.USE_RECAPTCHA is True:
                recaptcha_response = request.POST.get('g-recaptcha-response')
                url = 'https://www.google.com/recaptcha/api/siteverify'
                values = {
                    'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response
                }
                data = urllib.parse.urlencode(values).encode()
                req = urllib.request.Request(url, data=data)
                response = urllib.request.urlopen(req)
                recaptcha_result = json.loads(response.read().decode())
            else:
                recaptcha_result = {'success': True}
            if recaptcha_result['success'] is False:
                messages.error(
                    request, "Captcha failed, unable to generate new account")
                return (HttpResponseRedirect(reverse("index")))
            try:
                form.save()
            except IntegrityError:
                messages.error(request, "Email address already in use.")
                return render(request, template_name, {'form': form})
            new_user = auth.authenticate(username=request.POST['email'],
                                         password=request.POST['password1'])
            auth.login(request, new_user)
            if request.POST['next']:
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse("my_profile"))
    else:
        form = UserCreateForm(instance=User())

    context = {"form": form,
               "request": request}
    return render(request, template_name, context)


def view_profile(request, username=None):
    if not username:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse('login'), request.path))
        else:
            user = request.user
    else:
        user = get_object_or_404(User, username=username)
    return render(request, 'registration/profile.html', {'user': user})


@login_required
def edit_user(request):
    edit_form = UserEditForm(request.POST or None, instance=request.user)
    if request.method == "POST":
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse("my_profile"))
    return render(request, "registration/edit_user.html", {'form': edit_form})


def login(request):
    return render(request, 'login.html')


@login_required
def get_token(request):
    context = {'active': 'home'}
    if request.user.is_authenticated:
        token, created = Token.objects.get_or_create(user=request.user)
        context["token"] = token.key
    return render(request, 'registration/token.html', context)
