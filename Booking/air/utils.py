import json
import pycountry
from django.contrib.gis.geoip2 import GeoIP2
from air.constants.airports import AIRPORTS


def get_city_airport_list(data):
    result = []
    for i, val in enumerate(data):
        result.append({
            "iataCode": data[i]['iataCode'],
            "name": data[i]['name'],
            "cityName": data[i]['address']['cityName'],
            "countryName": data[i]['address']['countryName'],
        })
    return json.dumps(result)


def get_currency_by_country_name(country_name):
    country = pycountry.countries.get(name=country_name)
    currency = pycountry.currencies.get(numeric=country.numeric)
    return currency.alpha_3


def get_country_by_request(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    g = GeoIP2()
    try:
        location = g.country(ip)
    except Exception as e:
        location = None
    return location


def get_currency_code_by_request(request):
    currency_code = 'USD'
    location = get_country_by_request(request)
    if location:
        country_name = location["country_name"]
        country = pycountry.countries.get(name=country_name)
        currency = pycountry.currencies.get(numeric=country.numeric)
        currency_code = currency.alpha_3
    return currency_code


def form_traveler_parameters(adults, childes, infants):
    travelers = []
    if adults > 0:
        for i in range(1, adults + 1):
            travelers.append({
                "id": i,
                "travelerType": "ADULT"
            })
    if childes > 0:
        for i in range(adults + 1, adults + childes + 1):
            travelers.append({
                "id": i,
                "travelerType": "CHILD"
            })
    if infants > 0:
        for i in range(adults + childes + 1, adults + childes + infants + 1):
            travelers.append({
                "id": i,
                "travelerType": "SEATED_INFANT"
            })
    return travelers


def get_recommended_airport_from_country(country):
    country_name = country['country_name']
    for airport_code in AIRPORTS.keys():
        airport = AIRPORTS[airport_code]
        airport_country = airport['country'].lower()
        if airport_country.lower().startswith(country_name) or country_name.lower().startswith(airport_country):
            return f"{airport['code']} | {airport['airport']}, {airport['country']}"
