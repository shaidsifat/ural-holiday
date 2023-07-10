import ast
import json
from datetime import datetime
from pprint import pprint
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query_utils import FilteredRelation
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic.edit import FormView
from django.views import View


import stripe
from allauth.account.forms import LoginForm, SignupForm
from amadeus import Client, ResponseError, Location
from django_simple_coupons.models import Coupon, Ruleset
from django_simple_coupons.validations import validate_coupon

from booking_app.forms import ReSendCode, VerifyForm
from .templatetags.custom_func import base64_decode
from .constants.airports import AIRPORTS
from .models import FlightOffer, OrderDetail, Traveler
from .forms import SearchFlightForm, FlightSearchOrdersForm, SearchMultiFlightForm
from .utils import get_currency_code_by_request, form_traveler_parameters
from .utils import get_city_airport_list, get_currency_by_country_name, get_country_by_request
from .flight import Flight, construct_travelers

User = get_user_model()

amadeus = Client(client_id=settings.AMADEUS_API_KEY,
                 client_secret=settings.AMADEUS_API_SECRET,
                 hostname=settings.AMADEUS_HOSTNAME)


def get_access_for_order_manage(request):
    form = FlightSearchOrdersForm(request.POST)
    if form.is_valid():
        order_reference_id = form.cleaned_data['order_id']
        last_name = form.cleaned_data['last_name']
        order = OrderDetail.objects.filter(reference_id=order_reference_id).first()
        if order:
            primary_traveler = order.flight_offer.primary_traveler
            if primary_traveler.last_name == last_name:
                if request.user.is_authenticated:
                    order_manage_access = order.pk
                else:
                    order_manage_access = get_random_string(length=32)
                    request.session['order_manage_access'] = {
                        "key": order_manage_access,
                        "order_no": order.pk
                    }
                return JsonResponse({'success': True, 'order_manage_access': order_manage_access})
            else:
                errors = {"success": False, "message": "invalid_last_name"}
        else:
            errors = {"success": False, "message": "invalid_order"}
    else:
        errors = {"success": False, "message": "invalid_form_data", 'errors': request.form.errors}
    return JsonResponse(errors)


def order_manage(request):
    order_ref = request.GET.get('order_ref', None)
    order = None
    if order_ref and request.user.is_authenticated:
        order = OrderDetail.objects.filter(pk=order_ref).first()
    elif order_ref and 'order_manage_access' in request.session and request.session['order_manage_access']['key'] == order_ref:
        order = OrderDetail.objects.filter(pk=request.session['order_manage_access']['order_no']).first()

    if order:
        pass
        # try:
        #     amadeus_order = amadeus.booking.flight_order(order.reference_id).get()
        #     print(amadeus_order)
        # except ResponseError as error:
        #     print(error.response.result["errors"])
        #     messages.add_message(
        #         request, messages.ERROR, error.response.result["errors"][0]["detail"]
        #     )
        #     return redirect('home_page')
    else:
        return HttpResponseBadRequest()

    return render(request, 'air/order_manage.html', {
        "booking_ref": order.reference_id,
        "travelers": order.flight_offer.travelers.all(),
        "offer": Flight(order.flight_offer.flight).construct_flights()
    })


def flight_search_offers(request):
    location = get_country_by_request(request)
    post_data = []
    trips = request.GET.get('trips', '').strip(',').split(",")
    if len(trips) < 3:
        raise Http404

    start_date = ''
    end_date = ''
    lines = []
    return_date = request.GET.get('returnDate', '')
    for i in range(0, len(trips), 3):
        origin_code = trips[i]

        destination_code = trips[i + 1]

        depart_date = trips[i + 2]

        origin_dest = {
            "id": len(post_data) + 1,
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDateTimeRange": {
                "date": depart_date
            }
        }

        post_data.append(origin_dest)

        if len(lines) == 0 or lines[-1] != origin_code:
            lines.append(origin_code)
        lines.append(destination_code)

        if i == 0:
            start_date = depart_date
        if i >= len(trips) - 3:
            end_date = depart_date

    adults = int(request.GET.get('adults', 1))
    childes = int(request.GET.get('children', 0))
    infants = int(request.GET.get('infants', 0))
    travel_class = request.GET.get('travelClass', '')

    travelers = []
    if adults > 0:
        for i in range(1, adults + 1):
            travelers.append({"id": i, "travelerType": "ADULT"})
    if childes > 0:
        for i in range(adults + 1, adults + childes + 1):
            travelers.append({"id": i, "travelerType": "CHILD"})
    if infants > 0:
        for i in range(adults + childes + 1, adults + childes + infants + 1):
            travelers.append({"id": i, "travelerType": "SEATED_INFANT"})

    request_body = {
        "currencyCode": get_currency_by_country_name(location["country_name"]) if location else 'USD',
        "originDestinations": post_data,
        "travelers": travelers,
        "sources": ["GDS"],
        "searchCriteria": {"flightFilters": {}}
    }

    if return_date:
        request_body["searchCriteria"]["flightFilters"]["returnToDepartureAirport"] = True

    if travel_class:
        request_body["searchCriteria"]["flightFilters"]["cabinRestrictions"] = [{
            "cabin": travel_class,
            "originDestinationIds": [i for i in range(1, len(post_data) + 1)]
        }]

    try:
        search_flights = amadeus.shopping.flight_offers_search.post(request_body)
    except ResponseError as error:
        messages.add_message(request, messages.ERROR, error.response.result["errors"][0]["detail"])
        return redirect('home_page')

    search_flights_returned = []
    response = ""
    for flight in search_flights.data:
        offer = Flight(flight).construct_flights()
        search_flights_returned.append(offer)
        response = zip(search_flights_returned, search_flights.data)

    return render(request, "air/search_result.html", {
        "response": response,
        "lines": lines,
        "departureDate": start_date,
        "arrivalDate": end_date
    })


@cache_page(None)
def airport_search(request):
    if request.is_ajax():
        try:
            data = amadeus.reference_data.locations.get(keyword=request.GET.get('term', None),
                                                        subType=Location.ANY).data
        except ResponseError as error:
            return HttpResponseServerError(json.dumps(error), 'application/json')
        return HttpResponse(get_city_airport_list(data), 'application/json')


def book_travelers(request, flight):
    """Deprecated after refector book review page"""
    flight = ast.literal_eval(base64_decode(flight))
    offer = Flight(flight).construct_flights()

    if request.method == 'POST':
        travelers = construct_travelers(request.POST, flight["travelerPricings"])
        if len(travelers) > 0:
            with transaction.atomic():
                flight_offer = FlightOffer.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    name="-".join(offer['lines']),
                    price=offer['price'],
                    currency=offer['currency'],
                    flight=flight,
                    session_key=request.session.session_key
                )

                for traveler in travelers:
                    Traveler.objects.create(flight_offer=flight_offer, **traveler)

            return redirect('book_checkout', flight_offer_id=flight_offer.id)

    return render(request, 'air/traveler_info.html', {
        "flight": flight,
        "offer": offer,
    })


def book_checkout(request, flight_offer_id):
    if request.user.is_authenticated:
        flight_offer = get_object_or_404(FlightOffer, pk=flight_offer_id, user=request.user)
    else:
        flight_offer = get_object_or_404(FlightOffer, pk=flight_offer_id, session_key=request.session.session_key)

    try:
        if flight_offer.order and flight_offer.order.has_paid:
            raise Http404
    except OrderDetail.DoesNotExist as e:
        print(e)

    flight = flight_offer.flight

    try:
        flight_price_confirmed = amadeus.shopping.flight_offers.pricing.post(flight).data["flightOffers"]
    except ResponseError as error:
        messages.add_message(request, messages.ERROR, error.response.body)
        return redirect('home_page')

    offer = Flight(flight).construct_flights()
    coupon_code = ''
    discounted_value = offer['price']
    discount = None
    promo_code = request.GET.get('promo_code', None)
    print("my promo code is : ", promo_code)
    print("--------------------")
    print(promo_code)
    if promo_code and request.user.is_authenticated:
        status = validate_coupon(coupon_code=promo_code, user=request.user)
        if status['valid']:
            coupon = Coupon.objects.get(code=promo_code)
            coupon_code = coupon.code
            initial_value = float(offer['price'])
            discounted_value = "%.2f" % coupon.get_discounted_value(initial_value)
            discount = coupon.get_discount()
            # if discount['is_percentage']:
            #     discount_amount = (initial_value * discount['value']) / 100
            # else:
            #     discount_amount =  discount['value']

    return render(request, 'air/book_checkout.html', {
        "flight_offer_id": flight_offer_id,
        "flight": flight,
        "offer": offer,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "travelers": flight_offer.travelers.all(),
        "coupon_code": coupon_code,
        "discounted_value": discounted_value,
        'discount': discount
    })


@csrf_exempt
def create_checkout_session(request, flight_offer_id):
    promo_code = ''
    if request.user.is_authenticated:
        flight_offer = get_object_or_404(FlightOffer, pk=flight_offer_id, user=request.user)
        customer_email = request.user.email
        promo_code = request.GET.get('promo_code', '')
        discounted_value = flight_offer.price
        if promo_code:
            status = validate_coupon(coupon_code=promo_code, user=request.user)
            if status['valid']:
                coupon = Coupon.objects.get(code=promo_code)
                initial_value = float(flight_offer.price)
                discounted_value = float("%.2f" % coupon.get_discounted_value(initial_value))
    else:
        flight_offer = get_object_or_404(FlightOffer, pk=flight_offer_id, session_key=request.session.session_key)
        customer_email = flight_offer.primary_traveler.email_address
        discounted_value = flight_offer.price

    stripe.api_key = settings.STRIPE_SECRET_KEY
    paid_amount = int(discounted_value * 100)
    checkout_session = stripe.checkout.Session.create(
        customer_email=customer_email,
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': flight_offer.currency,
                    'product_data': {'name': flight_offer.name},
                    'unit_amount': paid_amount,
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(
            reverse('flight_payment_success')) + "?session_id={CHECKOUT_SESSION_ID}&promo_code=" + promo_code,
        cancel_url=request.build_absolute_uri(reverse('book_checkout', args=[flight_offer_id])),
    )

    try:
        if flight_offer.order:
            order = flight_offer.order
    except OrderDetail.DoesNotExist as e:
        order = OrderDetail()
        if request.user.is_authenticated:
            order.user = request.user
        else:
            order.user = None
        order.flight_offer = flight_offer

    order.stripe_payment_intent = checkout_session['payment_intent']
    order.amount = paid_amount
    order.save()

    return JsonResponse({'sessionId': checkout_session.id})


def payment_success(request):
    session_id = request.GET.get('session_id', None)
    order_id = request.GET.get('order_id', None)
    promo_code = request.GET.get('promo_code', '')

    if session_id is None and order_id is None:
        raise Http404

    if session_id:

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)

        order = get_object_or_404(OrderDetail, stripe_payment_intent=session.payment_intent)
        order.has_paid = True
        order.save()

        if promo_code and request.user.is_authenticated:
            status = validate_coupon(coupon_code=promo_code, user=request.user)
            if status['valid']:
                coupon = Coupon.objects.get(code=promo_code)
                coupon.use_coupon(user=request.user)

    if order_id:
        order = get_object_or_404(OrderDetail, pk=order_id)

    if not order.reference_id:
        try:
            flight_price_confirmed = amadeus.shopping.flight_offers.pricing.post(
                order.flight_offer.flight
            ).data["flightOffers"]

            flight_order = amadeus.booking.flight_orders.post(
                flight_price_confirmed, order.flight_offer.travelers_in_amadeus
            ).data
            order.reference_id = flight_order['id']
            order.reference_data = flight_order
            order.save()
        except ResponseError as error:
            messages.add_message(
                request, messages.ERROR, error.response.result["errors"][0]["detail"]
            )

    return render(request, "air/order_confirmation.html", {
        "booking_ref": order.reference_id,
        "travelers": order.flight_offer.travelers.all(),
        "offer": Flight(order.flight_offer.flight).construct_flights()
    })


def book_review(request, flight):
    print("flight", base64_decode(flight))
    flight = ast.literal_eval(base64_decode(flight))
    print("flight information===>", flight)
    offer = Flight(flight).construct_flights()
    print("offer information===>", offer)
    coupon_code = None
    discounted_value = None
    if request.user.is_authenticated:
        print("user is authenticated")
        # here get promo code for this user.
        coupon = Coupon.objects.annotate(
            allowed_users = FilteredRelation(
                'ruleset__allowed_users', condition=Q(ruleset__allowed_users__all_users = True ) | Q(ruleset__allowed_users__users__in = [request.user])
            )
        ).filter(ruleset__validity__is_active = True, ruleset__validity__expiration_date__gte = datetime.now()).first()

        if coupon:
            status = validate_coupon(coupon_code=coupon.code, user=request.user)
            print("status information ====>", status)
            if status['valid']:
                coupon_code = coupon.code
                discounted_value = "%.2f" % coupon.get_discounted_value(float(offer['price']))

    if request.method == 'POST':
        print("request method is POST")
        if not request.user.is_authenticated:
            print("request user is not authenticated")
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

        travelers = construct_travelers(request.POST, flight["travelerPricings"])
        print("travelers information ==>", travelers)

        if len(travelers) > 0:
            with transaction.atomic():
                flight_offer = FlightOffer.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    name="-".join(offer['lines']),
                    price=offer['price'],
                    currency=offer['currency'],
                    flight=flight,
                    session_key=request.session.session_key
                )
                print("flight_offer information ==>", flight_offer)

                for traveler in travelers:
                    Traveler.objects.create(flight_offer=flight_offer, **traveler)

            return redirect('book_checkout', flight_offer_id=flight_offer.id)

    return render(request, 'air/book_review.html', {
        "flight": flight,
        "offer": offer,
        "coupon_code": coupon_code,
        "discounted_value": discounted_value,
        "login_form": LoginForm(),
        "signup_form": SignupForm(),
        "verify_form": VerifyForm()
    })


def airports(request):
    """search airports by code, name, or country"""
    querying = request.GET.get('q')
    options = []
    if not querying:
        return JsonResponse({'results': AIRPORTS})

    codeFilter = list(filter(lambda item: item['code'].lower().find(querying.lower()) != -1, AIRPORTS.values()))
    airportFilter = list(filter(lambda item: item["airport"].lower().find(querying.lower()) != -1  , AIRPORTS.values()))
    countryFilter = list(filter(lambda item: item["country"].lower().find(querying.lower())!= -1 , AIRPORTS.values()))
    allFilter = []
    for item in codeFilter:
        code = item['code']
        name = item["airport"]
        country = item["country"]
        if {'id': code, 'text': f'{code} | {name}, {country}'} not in allFilter:
            allFilter.append({'id': code, 'text': f'{code} | {name}, {country}'})
    for item in airportFilter:
        code = item['code']
        name = item["airport"]
        country = item["country"]
        if {'id': code, 'text': f'{code} | {name}, {country}'} not in allFilter:
            allFilter.append({'id': code, 'text': f'{code} | {name}, {country}'})
    for item in countryFilter:
        code = item['code']
        name = item["airport"]
        country = item["country"]
        if {'id': code, 'text': f'{code} | {name}, {country}'} not in allFilter:
            allFilter.append({'id': code, 'text': f'{code} | {name}, {country}'})
    return JsonResponse({'results': allFilter})


class FlightSearchView(FormView):
    template_name = "air/flights.html"

    def get_form_class(self):
        type = self.get_form_type()
        if type == 'MULTI_WAY':
            return SearchMultiFlightForm
        return SearchFlightForm

    def get_form_type(self):
        return self.request.POST.get('multi_trip_type')

    def form_valid(self, form) -> HttpResponse:
        form_type = self.get_form_type()
        if form_type == 'MULTI_WAY':
            return self.handle_multiway_search(form)
        else:
            search_type = form.cleaned_data['trip_type']
            if search_type == 'ROUND_WAY':
                return self.handle_roundway_search(form)
            else:
                return self.handle_oneway_search(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["offers"] = []
        context["lines"] = []
        context["departureDate"] = ''
        context["arrivalDate"] = ''
        return context

    def _get_traveler_data_from_form(self, form):
        adults = form.cleaned_data['adults']
        child = form.cleaned_data['child']
        infant = form.cleaned_data['infant']
        travelers = form_traveler_parameters(adults, child, infant)
        return travelers

    def _get_flights_from_amadeus_api(self, form, origin, destination, departure_date):
        currency_code = get_currency_code_by_request(self.request)
        origin_destinations = [{
            'id': 1,
            'originLocationCode': origin.split("|")[0].strip(),
            'destinationLocationCode': destination.split("|")[0].strip(),
            'departureDateTimeRange': {
                'date': str(departure_date)
            }
        }]
        travelers = self._get_traveler_data_from_form(form)
        flight_class = form.cleaned_data['flight_class']

        request_body = {
            "currencyCode": currency_code,
            "originDestinations": origin_destinations,
            "travelers": travelers,
            "sources": ["GDS"],
            "searchCriteria": {
                "flightFilters": {
                    "cabinRestrictions": [{
                        "cabin": flight_class,
                        "originDestinationIds": [p['id'] for p in origin_destinations]
                    }]
                }
            }
        }

        try:
            amadeus = Client(
                client_id=settings.AMADEUS_API_KEY,
                client_secret=settings.AMADEUS_API_SECRET,
                hostname=settings.AMADEUS_HOSTNAME,
            )
            # modify request body to get only 3 first letters of originLocationCode and destinationLocationCode before search 
            request_body['originDestinations'][0]['originLocationCode'] = request_body['originDestinations'][0]['originLocationCode'][:3]
            request_body['originDestinations'][0]['destinationLocationCode'] = request_body['originDestinations'][0]['destinationLocationCode'][:3]
            search_flights = amadeus.shopping.flight_offers_search.post(request_body)
            return search_flights
        except ResponseError as error:
            print("error.response.result", error.response.result)
            messages.add_message(
                self.request, messages.ERROR, error.response.result["errors"][0]["detail"]
            )
            return redirect('home_page')

    def _sort_offers(self, offers, sort_by):
        if sort_by == 'price':
            return sorted(offers, key=lambda o: o['price'])
        elif sort_by == 'duration':
            return sorted(offers, key=lambda o: o['duration_in_minutes'])

    def _get_offers_by_airlines(self, offers):
        offers_by_airlines = {}
        for offer in offers:
            itinerary = offer['itineraries'][0]
            airline_code = itinerary['seg_first']['airline']
            from_airport, to_airport = itinerary['lines'][0], itinerary['lines'][-1]
            airline_offer: dict = offers_by_airlines.setdefault(airline_code, {})
            offers_key = f'{from_airport}-{to_airport}'
            existing_offers: list = airline_offer.setdefault(offers_key, [])
            existing_offers.append(offer)
        return offers_by_airlines

    def _create_combined_offer_by_airlines(self, all_offers, origin_airport: str, destination_airport: str):
        combined_offers = []
        offers_by_airlines = self._get_offers_by_airlines(all_offers)
        for _airline_code, airline_offers in offers_by_airlines.items():
            destination_offers = airline_offers.get(f"{origin_airport}-{destination_airport}", [])
            return_offers = airline_offers.get(f"{destination_airport}-{origin_airport}", [])


            if not destination_offers or not return_offers:
                # Skip airlines if they do not have destination or return offers
                continue

            for dest_offer in destination_offers:
                counter = 0
                for return_offer in return_offers:
                    if counter == 2:
                        # Combine same flight only twice while preparing round-way trip
                        counter = 0
                        break
                    offer = {
                        'price': dest_offer['price'] + return_offer['price'],
                        'duration_in_minutes': dest_offer['duration_in_minutes'] + return_offer['duration_in_minutes'],
                        'destination_offer': dest_offer,
                        'return_offer': return_offer,
                        'currency': dest_offer['currency'],
                    }
                    combined_offers.append(offer)
                    counter += 1
        return combined_offers

    def handle_multiway_search(self, form):
        currency_code = get_currency_code_by_request(self.request)
        adults = form.cleaned_data['multi_adults']
        child = form.cleaned_data['multi_child']
        infant = form.cleaned_data['multi_infant']
        travelers = form_traveler_parameters(adults, child, infant)

        flight_class = form.cleaned_data['multi_flight_class']
        offers = []
        for i in range(10):
            departure_name = "multi_departure_at_{}".format(i)
            arrival_name = "multi_arrival_at_{}".format(i)
            departure_date = "multi_departure_date_{}".format(i)

            departure_at = form.cleaned_data.get("multi_departure_at_{}".format(i),None)
            arrival_at = form.cleaned_data.get("multi_arrival_at_{}".format(i),None)
            if not departure_at  or not arrival_at:
                break
            origin_destinations = [{
                'id': 1,
                'originLocationCode': form.cleaned_data[departure_name].split("|")[0].strip(),
                'destinationLocationCode': form.cleaned_data[arrival_name].split("|")[0].strip(),
                'departureDateTimeRange': {
                    'date': str(form.cleaned_data[departure_date])
                }
            }]
            request_body = {
                "currencyCode": currency_code,
                "originDestinations": origin_destinations,
                "travelers": travelers,
                "sources": ["GDS"],
                "searchCriteria": {
                    "flightFilters": {
                        "cabinRestrictions": [{
                            "cabin": flight_class,
                            "originDestinationIds": [p['id'] for p in origin_destinations]
                        }]
                    }
                }
            }
            try:
                amadeus = Client(
                    client_id=settings.AMADEUS_API_KEY,
                    client_secret=settings.AMADEUS_API_SECRET,
                    hostname=settings.AMADEUS_HOSTNAME)
                search_flights = amadeus.shopping.flight_offers_search.post(request_body)
            except ResponseError as error:
                print(error)
                messages.add_message(
                    self.request, messages.ERROR, error.response.result["errors"][0]["detail"]
                )
                return redirect('home_page')
            lines = [form.cleaned_data[departure_name], form.cleaned_data[arrival_name]]
            sort_by = form.cleaned_data['multi_sort_by']
            for flight in search_flights.data:
                offer = Flight(flight).construct_flights()
                offer['flight'] = flight
                offers.append(offer)
            if sort_by == "price":
                offers.sort(key=lambda o: o['price'])
            elif sort_by == "duration":
                offers.sort(key=lambda o: o['duration_in_minutes'])

        return render(self.request, "air/flights.html", {
            "offers": offers,
            "lines": lines,
            "departureDate": str(form.cleaned_data['multi_departure_date_0']),
            "arrivalDate": str(form.cleaned_data['multi_departure_date_0']),
            "form": form,
        })

    def handle_roundway_search(self, form):
        form_origin: str = form.cleaned_data['departure_at']
        form_destination: str = form.cleaned_data['arrival_at']
        departure_date = form.cleaned_data['departure_date']
        return_date = form.cleaned_data['return_date']
        destination_flights = self._get_flights_from_amadeus_api(
            form,
            origin=form_origin,
            destination=form_destination,
            departure_date=departure_date,
        )
        return_flights = self._get_flights_from_amadeus_api(
            form,
            origin=form_destination,
            destination=form_origin,
            departure_date=return_date,
        )

        destination_offers = []
        for flight in destination_flights.data:
            flight['promo_code']  = form.cleaned_data['promo_code']
            offer = Flight(flight).construct_flights()
            offer['flight'] = flight
            destination_offers.append(offer)

        origin_offers = []
        for flight in return_flights.data:
            flight['promo_code']  = form.cleaned_data['promo_code']
            offer = Flight(flight).construct_flights()
            offer['flight'] = flight
            origin_offers.append(offer)

        sort_by = form.cleaned_data['sort_by']
        sorted_destination_offers = self._sort_offers(destination_offers, sort_by)
        sorted_origin_offers = self._sort_offers(origin_offers, sort_by)

        all_offers = self._sort_offers(sorted_destination_offers + sorted_origin_offers, sort_by)
        combined_offers = self._create_combined_offer_by_airlines(
            all_offers,
            origin_airport=form_origin.strip()[:3],
            destination_airport=form_destination.strip()[:3],
        )
        sorted_combined_offers = self._sort_offers(combined_offers, sort_by)
        lines = [form.cleaned_data['departure_at'], form.cleaned_data['arrival_at']]
        return render(self.request, "air/flights.html", {
            "offers": combined_offers,
            "lines": lines,
            "departureDate": str(form.cleaned_data['departure_date'].strftime("%d %b %y")),
            "arrivalDate": str(form.cleaned_data['return_date'].strftime("%d %b %y")),
            "form": form,
        })

    def handle_oneway_search(self, form):
        search_flights = self._get_flights_from_amadeus_api(
            form,
            form.cleaned_data['departure_at'],
            form.cleaned_data['arrival_at'],
            form.cleaned_data['departure_date'],
        )
        lines = [form.cleaned_data['departure_at'], form.cleaned_data['arrival_at']]

        offers = []
        for flight in search_flights.data:
            flight['promo_code']  = form.cleaned_data['promo_code']
            offer = Flight(flight).construct_flights()
            offer['flight'] = flight
            offers.append(offer)

        sort_by = form.cleaned_data['sort_by']
        sorted_offers = self._sort_offers(offers, sort_by)

        return render(self.request, "air/flights.html", {
            "offers": sorted_offers,
            "lines": lines,
            "departureDate": str(form.cleaned_data['departure_date'].strftime("%d %b %y")),
            "arrivalDate": str(form.cleaned_data['departure_date'].strftime("%d %b %y")),
            "form": form,
        })


def flights(request):
    if request.method == 'POST':
        type = request.POST.get('multi_trip_type')
        if type == 'MULTI_WAY':
            form = SearchMultiFlightForm(request.POST)
            if form.is_valid():
                currency_code = get_currency_code_by_request(request)
                adults = form.cleaned_data['multi_adults']
                child = form.cleaned_data['multi_child']
                infant = form.cleaned_data['multi_infant']
                travelers = form_traveler_parameters(adults, child, infant)

                flight_class = form.cleaned_data['multi_flight_class']
                offers = []
                for i in range(10):
                    departure_name = "multi_departure_at_{}".format(i)
                    arrival_name = "multi_arrival_at_{}".format(i)
                    departure_date = "multi_departure_date_{}".format(i)

                    departure_at = form.cleaned_data.get("multi_departure_at_{}".format(i),None)
                    arrival_at = form.cleaned_data.get("multi_arrival_at_{}".format(i),None)
                    if not departure_at  or not arrival_at:
                        break
                    origin_destinations = [{
                        'id': 1,
                        'originLocationCode': form.cleaned_data[departure_name].split("|")[0].strip(),
                        'destinationLocationCode': form.cleaned_data[arrival_name].split("|")[0].strip(),
                        'departureDateTimeRange': {
                            'date': str(form.cleaned_data[departure_date])
                        }
                    }]
                    request_body = {
                        "currencyCode": currency_code,
                        "originDestinations": origin_destinations,
                        "travelers": travelers,
                        "sources": ["GDS"],
                        "searchCriteria": {
                            "flightFilters": {
                                "cabinRestrictions": [{
                                    "cabin": flight_class,
                                    "originDestinationIds": [p['id'] for p in origin_destinations]
                                }]
                            }
                        }
                    }
                    try:
                        amadeus = Client(
                            client_id=settings.AMADEUS_API_KEY,
                            client_secret=settings.AMADEUS_API_SECRET,
                            hostname=settings.AMADEUS_HOSTNAME)
                        search_flights = amadeus.shopping.flight_offers_search.post(request_body)
                    except ResponseError as error:
                        print(error)
                        messages.add_message(
                            request, messages.ERROR, error.response.result["errors"][0]["detail"]
                        )
                        return redirect('home_page')
                    lines = [form.cleaned_data[departure_name], form.cleaned_data[arrival_name]]
                    sort_by = form.cleaned_data['multi_sort_by']
                    for flight in search_flights.data:
                        offer = Flight(flight).construct_flights()
                        offer['flight'] = flight
                        offers.append(offer)
                    if sort_by == "price":
                        offers.sort(key=lambda o: o['price'])
                    elif sort_by == "duration":
                        offers.sort(key=lambda o: o['duration_in_minutes'])

                return render(request, "air/flights.html", {
                    "offers": offers,
                    "lines": lines,
                    "departureDate": str(form.cleaned_data['multi_departure_date_0']),
                    "arrivalDate": str(form.cleaned_data['multi_departure_date_0']),
                    "form": form,
                })
        else:
            form = SearchFlightForm(request.POST)
            if form.is_valid():
                search_type = form.cleaned_data['trip_type']
                if search_type == "ROUND_WAY":
                    offers = []
                    #started roundway searching
                    currency_code = get_currency_code_by_request(request)
                    #split the post input to required format for AMADEUS API
                    origin_destinations1 = [{
                        'id': 1,
                        'originLocationCode': form.cleaned_data['departure_at'].split("|")[0].strip(),
                        'destinationLocationCode': form.cleaned_data['arrival_at'].split("|")[0].strip(),
                        'departureDateTimeRange': {
                            'date': str(form.cleaned_data['departure_date'])
                        }
                    }]
                    origin_destinations2 = [{
                        'id': 1,
                        'originLocationCode':form.cleaned_data['arrival_at'].split("|")[0].strip(),
                        'destinationLocationCode': form.cleaned_data['departure_at'].split("|")[0].strip() ,
                        'departureDateTimeRange': {
                            'date': str(form.cleaned_data['return_date'])
                        }
                    }]
                    adults = form.cleaned_data['adults']
                    child = form.cleaned_data['child']
                    infant = form.cleaned_data['infant']
                    travelers = form_traveler_parameters(adults, child, infant)
                    flight_class = form.cleaned_data['flight_class']

                    #departure date starter
                    request_body = {
                        "currencyCode": currency_code,
                        "originDestinations": origin_destinations1,
                        "travelers": travelers,
                        "sources": ["GDS"],
                        "searchCriteria": {
                            "flightFilters": {
                                "cabinRestrictions": [{
                                    "cabin": flight_class,
                                    "originDestinationIds": [p['id'] for p in origin_destinations1]
                                }]
                            }
                        }
                    }
                    try:
                        amadeus = Client(
                            client_id=settings.AMADEUS_API_KEY,
                            client_secret=settings.AMADEUS_API_SECRET,
                            hostname=settings.AMADEUS_HOSTNAME,
                        )
                        # modify request body to get only 3 first letters of originLocationCode and destinationLocationCode before search 
                        request_body['originDestinations'][0]['originLocationCode'] = request_body['originDestinations'][0]['originLocationCode'][:3]
                        request_body['originDestinations'][0]['destinationLocationCode'] = request_body['originDestinations'][0]['destinationLocationCode'][:3]
                        search_flights = amadeus.shopping.flight_offers_search.post(request_body)
                    except ResponseError as error:
                        print(error)
                        messages.add_message(
                            request, messages.ERROR, error.response.result["errors"][0]["detail"]
                        )
                        return redirect('home_page')

                    lines = [form.cleaned_data['departure_at'], form.cleaned_data['arrival_at']]
                    for flight in search_flights.data:
                        flight['promo_code']  = form.cleaned_data['promo_code']
                        offer = Flight(flight).construct_flights()
                        offer['flight'] = flight
                        offers.append(offer)

                    #departer date starter end

                    #return date starter 
                    request_body = {
                        "currencyCode": currency_code,
                        "originDestinations": origin_destinations2,
                        "travelers": travelers,
                        "sources": ["GDS"],
                        "searchCriteria": {
                            "flightFilters": {
                                "cabinRestrictions": [{
                                    "cabin": flight_class,
                                    "originDestinationIds": [p['id'] for p in origin_destinations2]
                                }]
                            }
                        }
                    }
                    try:
                        amadeus = Client(
                            client_id=settings.AMADEUS_API_KEY,
                            client_secret=settings.AMADEUS_API_SECRET,
                            hostname=settings.AMADEUS_HOSTNAME)
                        # modify request body to get only 3 first letters of originLocationCode and destinationLocationCode before search 
                        request_body['originDestinations'][0]['originLocationCode'] = request_body['originDestinations'][0]['originLocationCode'][:3]
                        request_body['originDestinations'][0]['destinationLocationCode'] = request_body['originDestinations'][0]['destinationLocationCode'][:3]
                        search_flights = amadeus.shopping.flight_offers_search.post(request_body)
                    except ResponseError as error:
                        print(error)
                        messages.add_message(
                            request, messages.ERROR, error.response.result["errors"][0]["detail"]
                        )
                        return redirect('home_page')

                    lines = [form.cleaned_data['departure_at'], form.cleaned_data['arrival_at']]

                    #return date starte end
                    sort_by = form.cleaned_data['sort_by']
                    for flight in search_flights.data:
                        flight['promo_code']  = form.cleaned_data['promo_code']
                        offer = Flight(flight).construct_flights()
                        offer['flight'] = flight
                        offers.append(offer)
                        
                    if sort_by == "price":
                        offers.sort(key=lambda o: o['price'])
                    elif sort_by == "duration":
                        offers.sort(key=lambda o: o['duration_in_minutes'])
                    
                    return render(request, "air/flights.html", {
                        "offers": offers,
                        "lines": lines,
                        "departureDate": str(form.cleaned_data['departure_date'].strftime("%d %b %y")),
                        "arrivalDate": str(form.cleaned_data['return_date'].strftime("%d %b %y")),
                        "form": form,
                    })


                else:
                    #started oneway searching 
                    currency_code = get_currency_code_by_request(request)
                    #split the post input to required format for AMADEUS API
                    origin_destinations = [{
                        'id': 1,
                        'originLocationCode': form.cleaned_data['departure_at'].split("|")[0].strip(),
                        'destinationLocationCode': form.cleaned_data['arrival_at'].split("|")[0].strip(),
                        'departureDateTimeRange': {
                            'date': str(form.cleaned_data['departure_date'])
                        }
                    }]
                    adults = form.cleaned_data['adults']
                    child = form.cleaned_data['child']
                    infant = form.cleaned_data['infant']
                    travelers = form_traveler_parameters(adults, child, infant)

                    flight_class = form.cleaned_data['flight_class']

                    request_body = {
                        "currencyCode": currency_code,
                        "originDestinations": origin_destinations,
                        "travelers": travelers,
                        "sources": ["GDS"],
                        "searchCriteria": {
                            "flightFilters": {
                                "cabinRestrictions": [{
                                    "cabin": flight_class,
                                    "originDestinationIds": [p['id'] for p in origin_destinations]
                                }]
                            }
                        }
                    }

                    try:
                        amadeus = Client(
                            client_id=settings.AMADEUS_API_KEY,
                            client_secret=settings.AMADEUS_API_SECRET,
                            hostname=settings.AMADEUS_HOSTNAME,
                        )
                        # modify request body to get only 3 first letters of originLocationCode and destinationLocationCode before search 
                        request_body['originDestinations'][0]['originLocationCode'] = request_body['originDestinations'][0]['originLocationCode'][:3]
                        request_body['originDestinations'][0]['destinationLocationCode'] = request_body['originDestinations'][0]['destinationLocationCode'][:3]
                        search_flights = amadeus.shopping.flight_offers_search.post(request_body)
                    except ResponseError as error:
                        print("error.response.result", error.response.result)
                        messages.add_message(
                            request, messages.ERROR, error.response.result["errors"][0]["detail"]
                        )
                        return redirect('home_page')

                    lines = [form.cleaned_data['departure_at'], form.cleaned_data['arrival_at']]

                    sort_by = form.cleaned_data['sort_by']
                    offers = []
                    for flight in search_flights.data:
                        flight['promo_code']  = form.cleaned_data['promo_code']
                        offer = Flight(flight).construct_flights()
                        offer['flight'] = flight
                        offers.append(offer)

                    if sort_by == "price":
                        offers.sort(key=lambda o: o['price'])
                    elif sort_by == "duration":
                        offers.sort(key=lambda o: o['duration_in_minutes'])
                    
                    return render(request, "air/flights.html", {
                        "offers": offers,
                        "lines": lines,
                        "departureDate": str(form.cleaned_data['departure_date'].strftime("%d %b %y")),
                        "arrivalDate": str(form.cleaned_data['departure_date'].strftime("%d %b %y")),
                        "form": form,
                    })
    else:
        form = SearchFlightForm()

    return render(request, "air/flights.html", {
        "offers": [],
        "lines": [],
        "departureDate": '',
        "arrivalDate": '',
        "form": form,
    })
