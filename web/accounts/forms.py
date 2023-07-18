from django import forms
from accounts.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = "__all__"

    def clean_password2(self):
        # Check that the two password entries match

        password1 = self.cleaned_data.get("password1", None)
        password2 = self.cleaned_data.get("password2", None)
        if password1 is not None:
            if password2 is None:
                raise ValidationError("Password Confirmation field is required.")
            if password1 and password2 and password1 != password2:
                raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        if self.cleaned_data["password2"]:
            user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    shopify_domain = forms.CharField(disabled=True, required=False)
    token = forms.CharField(disabled=True, required=False)

    class Meta:
        model = User
        fields = (
            "password",
            "is_active",
            "is_admin",
            "host",
        )
