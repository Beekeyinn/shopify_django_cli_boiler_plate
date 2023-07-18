import shopify
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.validators import validate_myshopify_domain

from core.models import ExtraFieldsModelsMixin


class UserManager(BaseUserManager):
    def create_user(self, shopify_domain, password=None, *args, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not shopify_domain:
            raise ValueError("ShopUsers must have a myshopify domain")

        user = self.model(shopify_domain=shopify_domain)

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, shopify_domain, password=None, *args, **kwargs):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            shopify_domain,
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(
    AbstractBaseUser,
    ExtraFieldsModelsMixin,
    PermissionsMixin,
):
    shopify_domain = models.CharField(
        verbose_name=_("Shopify Domain Name"),
        max_length=255,
        unique=True,
        db_index=True,
        validators=[validate_myshopify_domain],  # type: ignore
        help_text=_("Please provide the domain name only. Eg: example.myshopify.com"),
    )
    token = models.CharField(
        verbose_name=_("Shopify APP Token"),
        max_length=64,
        default="00000000000000000000000000000000",
    )
    access_scopes = models.TextField(
        verbose_name=_("Shopify Access Scope"),
        default=getattr(settings, "SHOPIFY_API_SCOPES"),
    )
    host = models.CharField(
        verbose_name=_("Shop ID"),
        max_length=100,
        default="000000000000000000000000000000",
    )
    is_active = models.BooleanField(verbose_name=_("Active"), default=True)
    is_admin = models.BooleanField(verbose_name=_("Admin"), default=False)

    objects = UserManager()

    USERNAME_FIELD = "shopify_domain"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.shopify_domain}"

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def session(self):
        return shopify.Session.temp(
            domain=self.shopify_domain,
            version=getattr(settings, "SHOPIFY_API_VERSION", "unstable"),
            token=self.token,
        )

    @classmethod
    def update_or_create(cls, shopify_session: shopify.Session, request):
        shop, created = cls.objects.update_or_create(
            shopify_domain=shopify_session.url,
            defaults={"token": shopify_session.token},
        )
        return shop
