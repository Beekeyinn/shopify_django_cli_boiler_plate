from shopify.utils import shop_url


def validate_myshopify_domain(value: str) -> str:
    try:
        normalized_domain = shop_url.sanitize_shop_domain(value)
    except Exception:
        raise ValueError("My Shopify Domain does not follow provided requirements.")
    else:
        if not normalized_domain:
            raise ValueError("My Shopify Domain does not follow provided requirements.")
        return value
