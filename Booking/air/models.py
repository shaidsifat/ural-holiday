from django.db import models
# from django.core import validators
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import re
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_phone_verified = models.BooleanField(default=False)


ADULT, CHILD, SENIOR, YOUNG, HELD_INFANT, SEATED_INFANT, STUDENT = "ADULT", "CHILD", "SENIOR", "YOUNG", "HELD_INFANT", "SEATED_INFANT", "STUDENT"

TRAVELER_TYPE = (
    (ADULT, _("Adult")),
    (CHILD, _("Child")),
    (SENIOR, _("Senior")),
    (YOUNG, _("Young")),
    (HELD_INFANT, _("Held Infant")),
    (SEATED_INFANT, _("Seated Infant")),
    (STUDENT, _("Student"))
)

ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST = "ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"

TRAVEL_CLASS = (
    (None, _("None")),
    (ECONOMY, _("Economy")),
    (PREMIUM_ECONOMY, _("Premium Economy")),
    (BUSINESS, _("Business")),
    (FIRST, _("First"))
)


FLIGHT_CLASS = (
    (ECONOMY, _("Economy")),
    (PREMIUM_ECONOMY, _("Premium Economy")),
    (BUSINESS, _("Business")),
    (FIRST, _("First"))
)


def get_traveler_type_label(_type):
    for key, label in TRAVELER_TYPE:
        if _type == key:
            return label

def get_traveler_class_label(_type):
    for key, label in TRAVEL_CLASS:
        if _type == key:
            return label


ONE_WAY = "ONE_WAY"
ROUND_WAY = "ROUND_WAY"
MULTI_WAY = "MULTI_WAY"

OFFER_TYPE = (
    (ONE_WAY, "One Way"),
    (ROUND_WAY, "Round Way"),
    (MULTI_WAY, "Multi Way"),
)

MALE, FEMALE = "MALE", "FEMALE"
GENDER = (
    (MALE, _("Male")),
    (FEMALE, _("Female"))
)

# Create your models here.
class FlightOffer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    # type= models.CharField(_("Offer Type"), choices=OFFER_TYPE, max_length=20, default=ONE_WAY)
    name = models.CharField(_("Name"), max_length=50, null=False)
    price = models.FloatField(verbose_name='Price')
    currency = models.CharField(
        _("Currency"),
        max_length=10,
        default="USD"
    )

    flight = models.JSONField(_("Flights"), default = dict)

    description = models.TextField(
        max_length=800,
        verbose_name='Description',
        null=True, blank=True
    )
    session_key = models.CharField(_("Session Key"), max_length=255, null=True, blank=True)

    created_on = models.DateTimeField(_("Date Created"), auto_now_add=True)

    @property
    def primary_traveler(self):
        return self.travelers.order_by('index').first()

    @property
    def travelers_in_amadeus(self):
        result = []
        for traveler in self.travelers.all():
            item =  {
                "id": traveler.index,
                "dateOfBirth": traveler.date_of_birth.isoformat(),
                "name": {
                    "firstName": traveler.first_name,
                    "lastName": traveler.last_name,
                    "middle_name": traveler.middle_name
                },
                "gender": traveler.gender,
                "contact": {
                    "emailAddress": traveler.email_address,
                    "phones": [traveler.phone_in_amadeus]
                }
            }

            item["documents"] = [
                {
                    "documentType": "PASSPORT",
                    # "birthPlace": "Madrid",
                    # "issuanceLocation": "Madrid",
                    "issuanceDate": traveler.passport_issue_date.isoformat(),
                    "number": traveler.passport_number,
                    "expiryDate": traveler.passport_expiry_date.isoformat(),
                    "issuanceCountry": traveler.passport_country,
                    "validityCountry": traveler.passport_country,
                    "nationality": traveler.passport_country,
                    "holder": True
                }
            ]
            result.append(item)
        return result

class OrderDetail(models.Model):

    # You can change as a Foreign Key to the user model
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )

    flight_offer = models.OneToOneField(
        FlightOffer,
        verbose_name='Flight offer',
        on_delete=models.PROTECT,
        related_name="order"
    )

    reference_id = models.CharField(_("Flight Order Reference ID"), max_length=255, null=True, blank=True)
    reference_data = models.JSONField(_("Flight Order Data"), default=dict, null=True, blank=True)

    amount = models.IntegerField(verbose_name='Amount')

    stripe_payment_intent = models.CharField( max_length=200)

    # This field can be changed as status
    has_paid = models.BooleanField(
        default=False,
        verbose_name='Payment Status'
    )

    created_on = models.DateTimeField(_("Date Created"), auto_now_add=True)
    updated_on = models.DateTimeField(_("Date Updated"), auto_now=True)

class Traveler(models.Model):
    index = models.CharField(_("Index in Offer"), max_length=5)
    flight_offer = models.ForeignKey(
        FlightOffer,
        on_delete=models.CASCADE,
        related_name="travelers"
    )
    date_of_birth = models.DateField(_("Date of Birth"))
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    middle_name = models.CharField(_("Middle Name"), max_length=255, null=True, blank=True)
    gender = models.CharField(_("Gender"), choices=GENDER, max_length=10, default=MALE)
    email_address = models.EmailField(_("Email Address"))
    phone = models.CharField(_("Phone"), max_length=50, null=True, blank=True)
    passport_number = models.CharField(_("Passport Number"), max_length=100, null=True, blank=False)
    passport_expiry_date = models.DateField(_("Passport Expire"), null=True, blank=True)
    type= models.CharField(_("Type"), choices=TRAVELER_TYPE, max_length=20, default=ADULT)
    country = models.CharField(_("Country"), max_length=50, null=True, blank=True)
    passport_issue_date = models.DateField(_("Passport Expire"), null=True, blank=True)
    passport_country = models.CharField(_("Passport Issue Country"), max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(_("Date Created"), auto_now_add=True)
    updated_on = models.DateTimeField(_("Date Updated"), auto_now=True)

    @property
    def phone_in_amadeus(self):
        re_obj = re.search("\(.*\)", self.phone)
        countryCallingCode = str(re_obj.group()[1:-2]).strip()
        number =  str(self.phone[re_obj.end():]).strip()
        return {
            "deviceType": "MOBILE",
            "countryCallingCode": countryCallingCode,
            "number": number
        }

    @property
    def get_type(self):
        for key, label in TRAVELER_TYPE:
            if self.type == key:
                return label
