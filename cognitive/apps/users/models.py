from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models

class User(AbstractUser):
    obfuscate = models.BooleanField(default=False)
    # 512 was what it is in old db
    interest_tags = models.CharField(max_length=512)
    org_id = models.CharField(max_length=36)
    old_id = models.CharField(max_length=36)

