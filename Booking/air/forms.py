import datetime
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import GENDER, MALE, FLIGHT_CLASS, OFFER_TYPE
MOST_SEGMENTS, AT_LEAST_ONE_SEGMENT, ALL_SEGMENTS = "MOST_SEGMENTS", "AT_LEAST_ONE_SEGMENT", "ALL_SEGMENTS"

COVERAGE_TYPE = (
    (MOST_SEGMENTS, _("Most Segments")),
    (AT_LEAST_ONE_SEGMENT, _("At least, one segment")),
    (ALL_SEGMENTS, _("All Segments"))
)

input_date_formats = ['%Y-%m-%d', '%m/%d/%Y','%m/%d/%y','%d %b %y']
class SearchFlightForm(forms.Form):
    today = timezone.now()
    after_week = today + datetime.timedelta(days=7)
    promo_code = forms.CharField(required=False)
    departure_at = forms.CharField(
        label="From",
        max_length=250,
        required=True,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'banner-input-form input-form',
                'placeholder': 'From'}))
    arrival_at = forms.CharField(
        label="To",
        max_length=250,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'banner-input-form input-to',
                'placeholder': 'To'}))
    trip_type = forms.ChoiceField(
        label="Trip",
        choices=OFFER_TYPE,
        widget=forms.Select(attrs={'class': 'trip-select'}))
    departure_date = forms.DateField(
        input_formats=input_date_formats,
        label="Depart",
        required=True,
        widget=forms.TextInput(
            attrs={
                'value': today.strftime("%d %b %y"),
                'autocomplete': 'off',
                'class': 'banner-form-datepicker-input',
            },
        ),
    )
    return_date = forms.DateField(
        input_formats=input_date_formats,
        label="Return",
        required=False,
        widget=forms.TextInput(
            attrs={
                'value': after_week.strftime("%d %b %y"),
                'autocomplete': 'off',
                'class': 'banner-form-datepicker-input'}))
    adults = forms.IntegerField(
        label="Adults",
        initial=1,
        min_value=1,
        max_value=9,
        required=True,
        widget=forms.NumberInput())
    child = forms.IntegerField(
        label="Children",
        initial=0,
        min_value=0,
        max_value=8,
        required=False,
        widget=forms.NumberInput())
    infant = forms.IntegerField(
        label="Infants",
        initial=0,
        min_value=0,
        max_value=1,
        required=False,
        widget=forms.NumberInput())

    flight_class = forms.ChoiceField(
        label="Flight Class",
        choices=FLIGHT_CLASS,
        initial='ECONOMY',
        widget=forms.RadioSelect(
            attrs={
                'class': 'passenger-class-flight-class'
            }
        ))
    sort_by = forms.CharField(
        label="Sort by",
        initial="price",
        required=True,
        widget=forms.HiddenInput(),
    )


class SearchMultiFlightForm(forms.Form):
    today = datetime.datetime.now()
    after_week = today + datetime.timedelta(days=7)

    multi_trip_type = forms.ChoiceField(
        label="Trip",
        choices=OFFER_TYPE,
        widget=forms.Select(attrs={'class': 'trip-select'}))
    multi_adults = forms.IntegerField(
        label="Adults",
        initial=1,
        min_value=1,
        max_value=9,
        required=True,
        widget=forms.NumberInput())
    multi_child = forms.IntegerField(
        label="Children",
        initial=0,
        min_value=0,
        max_value=8,
        required=False,
        widget=forms.NumberInput())
    multi_infant = forms.IntegerField(
        label="Infants",
        initial=0,
        min_value=0,
        max_value=1,
        required=False,
        widget=forms.NumberInput())

    multi_flight_class = forms.ChoiceField(
        label="Flight Class",
        choices=FLIGHT_CLASS,
        initial='ECONOMY',
        widget=forms.RadioSelect(
            attrs={
                'class': 'passenger-class-flight-class'
            }
        ))
    multi_sort_by = forms.CharField(
        label="Sort by",
        initial="price",
        required=False, widget=forms.HiddenInput())
    for i in range(5):
        locals()[f'multi_departure_at_{i}'] = forms.CharField(
            label="From",
            max_length=250,
            required=False if i > 1 else True,
            widget=forms.TextInput(attrs={
                'autocomplete': 'off',
                'class': 'banner-input-form input-form multi_departure_at',
                'placeholder': 'From'
            })
        )
        locals()[f'multi_arrival_at_{i}'] = forms.CharField(
            label="To",
            max_length=250,
            required=False if i > 1 else True,
            widget=forms.TextInput(attrs={
                'autocomplete': 'off',
                'class': 'banner-input-form input-to multi_arrival_at',
                'placeholder': 'To'
            })
        )
        locals()[f'multi_departure_date_{i}'] = forms.DateField(
            input_formats=input_date_formats,
            label="Depart",
            required=False if i > 1 else True,
            widget=forms.TextInput(attrs={
                'value': today.strftime("%d %b %y"),
                'autocomplete': 'off',
                'class': 'banner-form-datepicker-input'
            })
        )
        locals()[f'multi_return_date_{i}'] = forms.DateField(
            input_formats=input_date_formats,
            label="Return",
            required=False if i > 1 else True,
            widget=forms.TextInput(attrs={
                'value': after_week.strftime("%d %b %y"),
                'autocomplete': 'off',
                'class': 'banner-form-datepicker-input'
            })
        )


class FlightSearchOffersPostForm(forms.Form):
    currencyCode = forms.CharField(label='Currency code', max_length=10, required=False, initial="USD")
    # originDestinations
    # originDestinationid = forms.CharField(label='ID', max_length=100, required=True)
    originLocationCode = forms.CharField(
        label="Origin location",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'City, region, district or specific airport'})
    )
    destinationLocationCode = forms.CharField(
        label="Destination location",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'City, region, district or specific airport'})
    )
    departureDate = forms.DateField(input_formats=input_date_formats,label="Departing on", required=True)
    departureDateWindow = forms.IntegerField(
        label="",
        required=False,
        initial=0,
        help_text=_(
            "Either 1, 2 or 3 extra days around the local date (IxD for +/- x days - Ex: I3D), Either 1 to 3 days after the local date (PxD for +x days - Ex: P3D), or 1 to 3 days before the local date (MxD for -x days - Ex: M3D)")
    )
    departureTime = forms.TimeField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Select Time'}),
        input_formats=['%H:%M %p']
    )
    departureTimeWindow = forms.IntegerField(
        label="",
        required=False,
        initial=0,
        help_text=_("1 to 12 hours around (both +and -) the local time.")
    )
    arrivalDate = forms.DateField(input_formats=input_date_formats,label="Arriving on", required=False)
    arrivalDateWindow = forms.IntegerField(
        label="",
        required=False,
        initial=0,
        help_text=_(
            "Either 1, 2 or 3 extra days around the local date (IxD for +/- x days - Ex: I3D), Either 1 to 3 days after the local date (PxD for +x days - Ex: P3D), or 1 to 3 days before the local date (MxD for -x days - Ex: M3D)")
    )
    arrivalTime = forms.TimeField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Select Time'})
    )
    arrivalTimeWindow = forms.IntegerField(
        label="",
        required=False,
        initial=0,
        help_text=_("1 to 12 hours around (both +and -) the local time.")
    )
    adults = forms.IntegerField(label="Adults", initial=1, required=False)
    children = forms.IntegerField(label="Children", initial=0, required=False)
    infants = forms.IntegerField(label="Infants", initial=0, required=False)

    # # searchCriteria
    # excludeAllotments = forms.BooleanField(required=False, help_text=_("This option allows to exclude the isAllotment flag associated to a booking class in the search response when it exist."))
    # addOneWayOffers = forms.BooleanField(required=False, help_text=_("This option allows activate the one-way combinable feature"))
    # maxFlightOffers = forms.IntegerField(required=False, help_text=_("Maximum number of flight offers returned (Max 250)"))
    # maxPrice = forms.IntegerField(required=False, help_text=_("maximum price per traveler. By default, no limit is applied. If specified, the value should be a positive number with no decimals"))
    # allowAlternativeFareOptions = forms.BooleanField(required=False, help_text=_("This option allows to default to a standard fareOption if no offers are found for the selected fareOption."))
    # oneFlightOfferPerDay = forms.BooleanField(required=False, help_text=_("Requests the system to find at least one flight-offer per day, if possible, when a range of dates is specified. Default is false."))
    # ## additionalInformation
    # chargeableCheckedBags = forms.BooleanField(required=False, help_text=_("If true, returns the price of the first additional bag when the airline is an \"Amadeus Ancillary Services\" member."))
    # brandedFares = forms.BooleanField(required=False, help_text=_("If true, returns the fare family name for each flight-offer which supports fare family"))
    # ## pricingOptions
    # includedCheckedBagsOnly = forms.BooleanField(required=False, help_text=_("If true, returns the flight-offers with included checked bags only"))
    # refundableFare = forms.BooleanField(required=False, help_text=_("If true, returns the flight-offers with refundable fares only"))
    # noRestrictionFare = forms.BooleanField(required=False, help_text=_("If true, returns the flight-offers with no restriction fares only"))
    # noPenaltyFare = forms.BooleanField(required=False, help_text=_("If true, returns the flight-offers with no penalty fares only"))
    # ## flightFilters
    # crossBorderAllowed = forms.BooleanField(required=False, help_text=_("Allows to search a location outside the borders when a radius around a location is specified. Default is false."))
    # moreOvernightsAllowed = forms.BooleanField(required=False, help_text=_("This flag enables/disables the possibility to have more overnight flights in Low Fare Search"))
    # returnToDepartureAirport = forms.BooleanField(required=False, help_text=_("This option force to retrieve flight-offer with a departure and a return in the same airport"))
    # railSegmentAllowed = forms.BooleanField(required=False, help_text=_("This flag enable/disable filtering of rail segment (TGV AIR, RAIL ...)"))
    # maxFlightTime = forms.BooleanField(required=False, help_text=_("Maximum flight time as a percentage relative to the shortest flight time available for the itinerary"))
    # ### carrierRestrictions
    # blacklistedInEUAllowed = forms.BooleanField(required=False, help_text=_("This flag enable/disable filtering of blacklisted airline by EU. The list of the banned airlines is published in the Official Journal of the European Union, where they are included as annexes A and B to the Commission Regulation. The blacklist of an airline can concern all its flights or some specific aircraft types pertaining to the airline"))
    # #-excludedCarrierCodes = forms.JSONField()
    # #-includedCarrierCodes = forms.JSONField()
    # ### cabinRestrictions array[1 - 6]
    # cabin = forms.ChoiceField(choices=TRAVEL_CLASS, required=False, help_text=_("quality of service offered in the cabin where the seat is located in this flight. Economy, premium economy, business or first class"))
    # coverage = forms.ChoiceField(choices=COVERAGE_TYPE, required=False, help_text=_("part of the trip covered by the travel class restriction (ALL_SEGMENTS if ommited)"))
    # #- originDestinationIds = forms.JSONField()
    # ### connectionRestriction
    # maxNumberOfConnections = forms.IntegerField(required=False, help_text=_("The maximal number of connections for each itinerary. Value can be 0, 1 or 2."))
    # airportChangeAllowed = forms.BooleanField(required=False, help_text=_("Allow to change airport during connection"))
    # technicalStopsAllowed = forms.BooleanField(required=False, help_text=_("This option allows the single segment to have one or more intermediate stops (technical stops)."))

    def clean(self):
        cleaned_data = super().clean()
        originLocationCode = self.cleaned_data.get("originLocationCode")
        destinationLocationCode = self.cleaned_data.get("destinationLocationCode")
        if len(originLocationCode) < 2:
            raise ValidationError("Invalid origin location code")
        else:
            cleaned_data['originLocationCode'] = originLocationCode[:3]

        if len(destinationLocationCode) < 2:
            raise ValidationError("Invalid origin location code")
        else:
            cleaned_data['destinationLocationCode'] = destinationLocationCode[:3]

        return cleaned_data


class TravelerInfoForm(forms.Form):
    id = forms.CharField(label="Traveler ID", max_length=255, required=True)
    firstName = forms.CharField(label='First Name', max_length=255, required=True)
    lastName = forms.CharField(label='Last Name', max_length=255, required=True)
    middleName = forms.CharField(label="Middle Name", max_length=255, required=False)
    gender = forms.ChoiceField(label="Gender", choices=GENDER, initial=MALE, required=False)
    dateOfBirth = forms.DateField(label="Date of Birth", required=True)
    emailAddress = forms.EmailField(label="Email Field", required=True)
    country = forms.CharField(label="Country", max_length=50, required=True)
    phoneCountryCode = forms.CharField(label="Phone Country Code", max_length=10, required=True)
    phoneNumber = forms.CharField(label="Phone Number", max_length=50, required=True)
    passportNumber = forms.CharField(label="Passport Number", max_length=100, required=False)
    passportIssueDate = forms.DateField(label="Passport Issue Date", required=False)
    passportExpiryDate = forms.DateField(label="Passport Expire Date", required=False)
    passportCountry = forms.CharField(label="Passport Country", max_length=50, required=True)
    type = forms.CharField(label="Type", max_length=50, required=True)


class FlightSearchOrdersForm(forms.Form):
    order_id = forms.CharField(label="Order Reference ID", max_length=255, required=True)
    last_name = forms.CharField(label="Last Name", max_length=255, required=True)
