from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .settings.utils import get_secret

TWILIO_VERIFY_SERVICE_SID=get_secret('TWILIO_VERIFY_SERVICE_SID')
TWILIO_ACCOUNT_SID=get_secret('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=get_secret('TWILIO_AUTH_TOKEN')


def send(phone):
    print("Send confirmation code to ", phone)
    # client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # verify = client.verify.services(TWILIO_VERIFY_SERVICE_SID)
    # verify.verifications.create(to=phone, channel='sms')


def check(phone, code):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # verify = client.verify.services(TWILIO_VERIFY_SERVICE_SID)
    # try:
    #     result = verify.verification_checks.create(to=phone, code=code)
    # except TwilioRestException:
    #     return False
    # return result.status == 'approved'
    return True
