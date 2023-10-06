from celery import current_app
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


@current_app.task(
    bind=True,
    name="send-uninstallation-email",
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 10},
)
def send_uninstallation_message(self, information):
    context = {"information": information}
    email_message = EmailMultiAlternatives()
    email_message.subject = "We're sorry to see you go, but we're here for you!"
    email_message.from_email = getattr(settings, "EMAIL_HOST_USER")

    body_text = get_template("emails/uninstallation.txt").render(context)
    html_text = get_template("emails/uninstallation.html").render(context)

    email_message.to = [information.get("email", None)]
    email_message.body = body_text
    email_message.attach_alternative(html_text, "text/html")
    email_message.send(fail_silently=False)
    return f"Email send to {information.get('email',None)}"
