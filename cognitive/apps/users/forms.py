from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from cognitive.apps.users.models import User

from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, TabHolder, Tab, StrictButton
from crispy_forms.layout import Layout, HTML, Button, Row, Field, Hidden
from crispy_forms.helper import FormHelper


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "interest_tags",
                  "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = user.email
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):

        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['interest_tags'].label = "Interests"
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout()
        tab_holder = TabHolder()


class UserEditForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = user.email
        if commit:
            user.save()
        return user

    def clean_password(self):
        return ""

    def __init__(self, *args, **kwargs):

        super(UserEditForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout()
        tab_holder = TabHolder()
