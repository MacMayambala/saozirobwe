

######################################################################################################
from django.core.management.base import BaseCommand
from Munomukabi.models import Member
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)

# === SMS Sending Function ===
def send_sms_speedamobile(phone_number, message_text):
    url = "http://apidocs.speedamobile.com/api/SendSMS"
    payload = {
        "api_id": "API67606975827",  # 🔥 Replace with your actual SpeedaMobile API ID
        "api_password": "Admin@sao256",  # 🔥 Replace with your API Password
        "sms_type": "P",  # 'T' = Transactional
        "encoding": "T",  # 'T' = Text
        "sender_id": "BULKSMS", # 🔥 Replace with your registered Sender ID
        "phonenumber": phone_number,  # Must be 2567XXXXXXX
        "textmessage": message_text,
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"SMS API error: {str(e)}")
        return {"status": "F", "remarks": str(e)}


# === Main Command Class ===
class Command(BaseCommand):
    help = 'Notify members with expired status by email and SMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug-email',
            action='store_true',
            help='Send all emails to a test address for debugging',
        )

    def handle(self, *args, **kwargs):
        debug_mode = kwargs.get('debug_email', False)
        today = timezone.now().date()
        expired_members = Member.objects.filter(status='expired')

        self.stdout.write(f"Found {expired_members.count()} expired members.")

        if not expired_members.exists():
            self.stdout.write("No expired members found.")
            return

        # Log email settings for debugging
        self.stdout.write(f"Email backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Email host: {settings.EMAIL_HOST}")
        self.stdout.write(f"Email port: {settings.EMAIL_PORT}")
        self.stdout.write(f"Email use TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"Email use SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        self.stdout.write(f"Default from email: {settings.DEFAULT_FROM_EMAIL}")

        for member in expired_members:
            customer = member.customer

            # === Prepare email content ===
            context = {
                "first_name": customer.first_name,
                "surname": customer.surname,
                "member_number": customer.member_number,
                "subscription_start": member.subscription_start,
                "subscription_end": member.subscription_end,
                #"logo_url": f"{settings.STATIC_URL}logo.png",  # Use settings for URL
            }
            html_content = render_to_string("email/expiry_email.html", context)
            text_content = strip_tags(html_content)

            # === Send Email ===
            if customer.email:
                # Use a consistent from_email that matches your mail server settings
                from_email = "Sao Zirobwe Sacco<noreply@saozirobwe.co.ug>"
                
                # If in debug mode, redirect to test email
                to_email = "your-test-email@example.com" if debug_mode else customer.email
                
                email = EmailMultiAlternatives(
                    subject="Munomukabi Membership Expired",
                    body=text_content,
                    from_email=from_email,
                    to=[to_email],
                    # You might need to specify reply-to or add headers
                    headers={'Reply-To': 'info@saozirobwe.co.ug'}
                )
                email.attach_alternative(html_content, "text/html")
                
                try:
                    email.send(fail_silently=False)
                    self.stdout.write(f"✅ Email sent to {to_email}")
                except Exception as e:
                    # Detailed error logging
                    logger.error(f"Email error for {customer.email}: {str(e)}")
                    self.stdout.write(f"❌ Failed to send email to {to_email}: {str(e)}")
            else:
                self.stdout.write(f"⚠️ No email for {customer.cus_id} - Skipped email.")

            # === Send SMS ===
            if customer.phone_number1:
                sms_message = f"SAO ZIROBWE\nDear {customer.first_name},\nMunomukabi Wo Yagwako nga {member.subscription_end}.\nTukusaba Omuzebujja Okusobola okuganyurwa mumpereza Enno."
                sms_message += "\nFor more information, please contact us at 0392984288.\n\nThank you."
                sms_message += "\nSAO ZIROBWE SACCO\n\nThis is an automated message. Please do not reply."
                
                sms_result = send_sms_speedamobile(customer.phone_number1, sms_message)
                
                if sms_result.get("status") == "S":
                    self.stdout.write(f"✅ SMS sent to {customer.phone_number1}")
                else:
                    self.stdout.write(f"❌ Failed to send SMS to {customer.phone_number1}: {sms_result.get('remarks')}")
            else:
                self.stdout.write(f"⚠️ No phone number for {customer.cus_id} - Skipped SMS.")