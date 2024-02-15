import os
import random
from mailjet_rest import Client
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

load_dotenv()


def send_otp_to_email(email):
    api_key = os.environ["API_KEY"]
    api_secret = os.environ["API_SECRET"]
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    subject = "Your account verification email"
    otp = random.randint(100000, 999999)
    message = f"Your otp is {otp}"

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "vkoesko@gmail.com",
                },
                "To": [
                    {
                        "Email": email,
                    }
                ],
                "Subject": subject,
                "TextPart": message,
            }
        ]
    }

    mailjet.send.create(data=data)

    user = get_user_model().objects.get(email=email)
    user.otp = otp
    user.save()
