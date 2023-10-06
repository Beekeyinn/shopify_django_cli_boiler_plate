import logging
import shopify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


from accounts.models import User

from profiles.models import Profile

logger = logging.getLogger("accounts")


@receiver(post_save, sender=User)
def populate_profile(
    instance: User, created: bool, sender: User, *args, **kwargs
) -> None:
    if created and not instance.is_superuser:
        fullname = "shopify"
        if not hasattr(instance, "profile"):
            with instance.session:
                shop = shopify.Shop.current()
                fullname = shop.shop_owner
                first_name, last_name = shop.shop_owner.split()
                try:
                    profile, created = Profile.objects.get_or_create(
                        user=instance,
                        first_name=first_name,
                        last_name=last_name,
                        shop_name=shop.name,
                        phone_number=shop.phone,
                        country=shop.country_name,
                        email=shop.email,
                        review_on=timezone.now() + timezone.timedelta(days=2),
                    )
                except Exception as e:
                    logger.error("Shopify Exception: ", exc_info=e)
