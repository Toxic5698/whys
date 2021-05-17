from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ImportDataForm(forms.Form):
    # file_import = ...
    text_import = forms.CharField()

    class Meta:
        fields = [
            # 'file_import',
            'text_import'
        ]


class ProductSearchForm(forms.Form):
    q = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["q"].label = "Zadejte hledany vyraz"
        self.fields["q"].widget.attrs.update({"class": "form-control"})
