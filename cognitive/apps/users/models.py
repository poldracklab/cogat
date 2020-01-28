from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.urls import reverse
from django.db import models


class User(AbstractUser):
    obfuscate = models.BooleanField(default=False)
    interest_tags = models.TextField(blank=True)
    specialist_tags = models.TextField(blank=True)
    old_id = models.CharField(max_length=36, blank=True)
    org_id = models.CharField(max_length=36, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    rank = models.CharField(max_length=10, default="3")

    def save(self, *args, **kwargs):
        notify = False
        if self.pk is None:
            notify = True

        super(User, self).save(*args, **kwargs)

        if notify:
            new_user_notify(self)


def new_user_notify(user):
    subject = "New User Registered for Cognitive Atlas"
    body = '''
    <p>Email: {}</p>
    <p>First Name: {}</p>
    <p>Last Name: {}</p>
    <p>Interests: {}</p>
    '''.format(user.email, user.first_name, user.last_name, user.interest_tags)
    send_mail(subject, "", "newuser@cognitiveatlas.org",
              settings.NOTIFY_EMAILS, html_message=body)
