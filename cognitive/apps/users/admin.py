from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from cognitive.apps.users.models import User


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('obfuscate', 'interest_tags', 'specialist_tags',
                           'old_id', 'org_id', 'title', 'rank')}),
    )


admin.site.register(User, CustomUserAdmin)
