from django.views.generic import TemplateView
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^api$', views.api, name="api"),
    url(r'^about$', views.about, name="about"),
    url(r'^403$', TemplateView.as_view(template_name='403.html')),
    url(r'^results$', TemplateView.as_view(template_name='main/results.html')),
]
