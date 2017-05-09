from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models

class User(AbstractUser):
    obfuscate = models.BooleanField(default=False)
    interest_tags = models.TextField(blank=True)
    specialist_tags = models.TextField(blank=True)
    old_id = models.CharField(max_length=36, blank=True)
    org_id = models.CharField(max_length=36, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
