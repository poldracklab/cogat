from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(), name="login"),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name="logout"),
    url(r'^create/$', views.create_user, name="create_user"),
    url(r'^password/$', auth_views.PasswordChangeView.as_view(),
        name='password_change'),
    url(r'^password/change/done/$', auth_views.PasswordChangeDoneView.as_view(),
        name='password_change_done'),
    url(r'^password/reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    url(r'^password/reset/complete/$', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^profile/edit$', views.edit_user, name="edit_user"),
    url(r'^profile/.*$', views.view_profile, name="my_profile"),
    url(r'^token/$', views.get_token, name="token"),
    url(r'^(?P<username>[A-Za-z0-9@/./+/-/_]+)/$', views.view_profile,
        name="profile"),
]
