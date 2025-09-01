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
    


from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from staff_management.models import Staff, Leave
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Notify staff about upcoming leave end dates (7 or 1 day remaining)'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        leaves = Leave.objects.filter(status='Approved', end_date__gte=today)

        self.stdout.write(f"Processing {leaves.count()} approved leave records for reminders...")

        for leave in leaves:
            staff = leave.staff
            remaining_days = leave.remaining_days

            if remaining_days in [1, 7]:
                subject = f"Leave Ending Soon - {leave.leave_type}"
                message_text = f"Dear {staff.full_name},\n\nYour {leave.leave_type} leave will end in {remaining_days} day(s) on {leave.end_date}."
                contact_info = f"Contact: {staff.phone}"
                if staff.next_of_kin_phone:
                    contact_info += f" | Emergency: {staff.next_of_kin_phone}"
                message_text += f"\n{contact_info}\nSAO ZIROBWE SACCO"

                if staff.email:
                    try:
                        context = {
                            "first_name": staff.first_name,
                            "last_name": staff.last_name,
                            "leave_type": leave.leave_type,
                            "start_date": leave.start_date,
                            "end_date": leave.end_date,
                            "status": leave.status,
                            "remaining_days": remaining_days,
                        }
                        html_content = render_to_string("email/leave_notification.html", context)
                        text_content = strip_tags(html_content)
                        email = EmailMultiAlternatives(
                            subject=subject,
                            body=text_content,
                            from_email="Sao Zirobwe Sacco <noreply@saozirobwe.co.ug>",
                            to=[staff.email],
                            headers={'Reply-To': 'info@saozirobwe.co.ug'}
                        )
                        email.attach_alternative(html_content, "text/html")
                        email.send(fail_silently=False)
                        self.stdout.write(f"✅ Reminder email sent to {staff.email}")
                    except Exception as e:
                        logger.error(f"Failed to send reminder email to {staff.email}: {str(e)}")
                        self.stdout.write(f"❌ Failed to send reminder email to {staff.email}: {str(e)}")

                if staff.phone:
                    sms_result = send_sms_speedamobile(staff.phone, message_text)
                    if sms_result.get("status") == "S":
                        self.stdout.write(f"✅ Reminder SMS sent to {staff.phone}")
                    else:
                        self.stdout.write(f"❌ Failed to send reminder SMS to {staff.phone}: {sms_result.get('remarks')}")
                logger.info(f"Reminder sent for leave {leave.id} to {staff.full_name}: {remaining_days} day(s) remaining")
            else:
                self.stdout.write(f"No reminder needed for leave {leave.id} (remaining: {remaining_days} days)")