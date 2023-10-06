from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from base.models import ExtraFieldsModelsMixin


# Create your models here.
class Profile(ExtraFieldsModelsMixin, models.Model):
    user = models.OneToOneField(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="profile",
        db_index=True,
    )
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    shop_name = models.CharField(_("Shop Name"), max_length=100)
    phone_number = models.CharField(_("Phone Number"), max_length=15, null=True)
    country = models.CharField(_("Country"), max_length=50)
    email = models.EmailField(_("Email"), max_length=254)
    tutorial = models.BooleanField(default=True)
    reviewed = models.BooleanField(default=False)
    review_on = models.DateTimeField(null=True, blank=False)

    def __str__(self) -> str:
        return f"{self.fullname} {self.email}"

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"
