import re
from datetime import datetime
from .forms import TravelerInfoForm, MALE
from .models import get_traveler_type_label, get_traveler_class_label
from .constants.airlines import AIRLINES
class Flight:
    def __init__(self, flight):
        self.flight = flight

    def construct_flights(self):
        offer = {
            'id': self.flight['id'],
            'price': float(self.flight['price']['total']),
            'currency': self.flight['price']['currency'],
            'traveler_count': len(self.flight['travelerPricings']),
            'bookable_seats': self.flight.get('numberOfBookableSeats', None), "itineraries": [],
            'fareType': self.flight['pricingOptions']['fareType'][0]
        }
        offer['departureDate'], _ = parse_datetime(self.flight['itineraries'][0]['segments'][0]['departure']['at'])
        offer['arrivalDate'], _ = parse_datetime(self.flight['itineraries'][-1]['segments'][-1]['arrival']['at'])
        offer['lines'] = []
        offer_index = 0
        segments_by_id = {}

        segments_pricing = get_segments_pricing(self.flight['travelerPricings'])

        total_duration_in_minutes = 0

        for itinerary_item in self.flight['itineraries']:
            segments = []
            segment_index = 0
            lines = []
            for s in itinerary_item['segments']:
                
                depart_date, depart_hour = parse_datetime(s['departure']['at'])
                arrival_date, arrival_hour = parse_datetime(s['arrival']['at'])

                arrival_duration = s.get('duration', '')[2:]
                arrival_duration = arrival_duration.lower()
                arrival_duration_array = arrival_duration.split('h')
                if len(arrival_duration_array) > 1:
                    arrival_duration = f'{arrival_duration_array[0]}h {arrival_duration_array[1]}'
                else:
                    arrival_duration = arrival_duration_array[0]

                included_checked_bags = segments_pricing[s['id']]['includedCheckedBags']
                weight = included_checked_bags.get('weight', '')
                unit = included_checked_bags.get('weightUnit', '').lower()
                included_checked_bags = f"{weight}{unit}"

                airline = s['carrierCode']
                imgcode = AIRLINES.get(airline, {}).get('imgcode', None) if AIRLINES.get(airline, {}).get('imgcode', None) else s['carrierCode']
                seg_info = {
                    "id": s['id'],
                    "departureAirport": s['departure']['iataCode'],
                    "airlineLogo": get_airline_logo(imgcode),
                    "airline": s['carrierCode'],
                    "airline_name": AIRLINES.get(airline, {}).get('name', airline),
                    "departureAt": get_time(s['departure']['at']),
                    "departureDate": depart_date,
                    "departureHour": depart_hour,
                    "arrivalAirport": s['arrival']['iataCode'],
                    "arrivalAt": get_time(s['arrival']['at']),
                    "arrivalDate": arrival_date,
                    "arrivalHour": arrival_hour,
                    "arrivalDuration": arrival_duration,
                    "cabin": segments_pricing[s['id']]['cabin'].lower(),
                    "includedCheckedBags": included_checked_bags,
                }
                segments_by_id[s['id']] = seg_info

                if len(lines) == 0 or lines[-1] != seg_info['departureAirport']:
                    lines.append(seg_info['departureAirport'])
                lines.append(seg_info['arrivalAirport'])

                segment_index += 1
                if segment_index >= len(itinerary_item['segments']):
                    segments.append(seg_info)
                    break
                else:
                    seg_info["stop_time"] = get_stoptime(itinerary_item['duration'], s["duration"],
                                                         itinerary_item['segments'][segment_index]["duration"])
                    segments.append(seg_info)

            if len(offer['lines']) == 0 or offer['lines'][-1] != segments[0]['departureAirport']:
                offer['lines'].append(segments[0]['departureAirport'])
            offer['lines'].append(segments[-1]['arrivalAirport'])

            total_duration = itinerary_item['duration'][2:]
            total_duration = total_duration.lower()
            total_duration_array = [i for i in total_duration.split('h') if i != '']
            if len(total_duration_array) > 1:
                hours = int(total_duration_array[0])
                minutes = int(total_duration_array[1][:-1])
                total_duration = f'{hours}h {minutes}m'
                total_duration_in_minutes = hours * 60 + minutes
            else:
                hours = int(total_duration_array[0])
                total_duration = f'{hours}h'
                total_duration_in_minutes = hours * 60

            prices = [{'travelerType': p['travelerType'], **p['price']} for p in self.flight['travelerPricings']]

            airline = segments[0].get('airline')
            seg_first = {
                "airline_name": AIRLINES.get(airline, {}).get('name', airline),
                **segments[0]
            }
            airline = segments[-1].get('airline')
            seg_last = {
                "airline_name": AIRLINES.get(airline, {}).get('name', airline),
                **segments[-1]
            }

            itinerary = {
                "lines": lines,
                "seg_first": seg_first,
                "seg_last": seg_last,
                "numberOfStops": len(itinerary_item['segments']) - 1,
                "type": str(offer_index + 1) + ". Way",
                "totalDuration": total_duration,
                "segments": segments,
                "prices": prices
            }
            offer["itineraries"].append(itinerary)
            offer_index += 1

        offer['duration_in_minutes'] = total_duration_in_minutes

        offer['prices'] = []

        fare_detail_by_segment = {}
        for t in self.flight['travelerPricings']:
            travelerType = get_traveler_type_label(t['travelerType'])
            prices = {
                "currency": t['price']['currency'],
                "travelerType": travelerType,
                "toal": t['price']['total'],
                "base": t['price']['base'],
                "fees": sum_amount(t['price'].get('fees', [])),
                "taxes": sum_amount(t['price'].get('taxes', []))
            }
            offer['prices'] = prices

            for fare_detail in t['fareDetailsBySegment']:
                seg = segments_by_id[fare_detail['segmentId']]
                if seg['id'] not in fare_detail_by_segment:
                    fare_detail_by_segment[seg['id']] = {}
                fare_detail_by_segment[seg['id']]['name'] = f'{seg["departureAirport"]} - {seg["arrivalAirport"]}'
                if 'travelers' not in fare_detail_by_segment[seg['id']]:
                    fare_detail_by_segment[seg['id']]['travelers'] = {}
                fare_detail_by_segment[seg['id']]['travelers'][t['travelerId']] = {
                    "travelerType": travelerType,
                    "cabin": get_traveler_class_label(fare_detail['cabin']),
                    "fareBasis": fare_detail['fareBasis'],
                    "weight": fare_detail['includedCheckedBags'].get('weight', '-') if 'includedCheckedBags' in fare_detail else '-',
                    "weightUnit": fare_detail['includedCheckedBags'].get('weightUnit', '-') if 'includedCheckedBags' in fare_detail else '-',
                    "quantity": fare_detail['includedCheckedBags'].get('quantity', 0) if 'includedCheckedBags' in fare_detail else '-'
                }
        offer['fare_detail_by_segment'] = fare_detail_by_segment
        return offer


def sum_amount(_arr):
    _total = 0
    for _a in _arr:
        _total = _total + _a['amount']
    return _total


def get_airline_logo(carrier_code):
    return "https://s1.apideeplink.com/images/airlines/" + carrier_code + ".png"


def get_segments_pricing(travelers_prices):
    """get segments' pricing info by ID"""
    pricing_info = {}
    for traveler in travelers_prices:
        for segment in traveler['fareDetailsBySegment']:
            pricing_info[segment['segmentId']] = segment

    return pricing_info


def get_time(datetime_str):
    """parse datetime string"""
    return datetime.strptime(datetime_str[0:19], "%Y-%m-%dT%H:%M:%S")


def parse_datetime(date_time):
    dt_obj = datetime.strptime(date_time[0:19], "%Y-%m-%dT%H:%M:%S")
    return dt_obj.strftime("%Y-%m-%d"), dt_obj.strftime("%H:%M")


def get_stoptime(total_duration, first_flight_duration, second_flight_duration):
    if re.search('PT(.*)H', total_duration) is None:
        total_duration_hours = 0
    else:
        total_duration_hours = int(re.search('PT(.*)H', total_duration).group(1))
    if re.search('H(.*)M', total_duration) is None:
        total_duration_minutes = 0
    else:
        total_duration_minutes = int(re.search('H(.*)M', total_duration).group(1))

    if re.search('PT(.*)H', first_flight_duration) is None:
        first_flight_hours = 0
    else:
        first_flight_hours = int(re.search('PT(.*)H', first_flight_duration).group(1))
    if re.search('H(.*)M', first_flight_duration) is None:
        first_flight_minutes = 0
    else:
        first_flight_minutes = int(re.search('H(.*)M', first_flight_duration).group(1))

    if re.search('PT(.*)H', second_flight_duration) is None:
        second_flight_hours = 0
    else:
        second_flight_hours = int(re.search('PT(.*)H', second_flight_duration).group(1))
    if re.search('H(.*)M', second_flight_duration) is None:
        second_flight_minutes = 0
    else:
        second_flight_minutes = int(re.search('H(.*)M', second_flight_duration).group(1))

    connection_minutes = (total_duration_hours*60+total_duration_minutes) - (first_flight_hours*60 + first_flight_minutes + second_flight_hours*60 + second_flight_minutes)
    hours = connection_minutes // 60
    minutes = connection_minutes % 60
    return str(hours) + 'h ' + str(minutes) + 'm'


def construct_travelers(data, flight_pricing):
    temp = {}
    available_ids = [fp["travelerId"] for fp in flight_pricing]
    for key in data:
        t = str(key).split("_")
        if len(t) == 2 and t[1] in available_ids:
            traveler_info_key = t[0]
            if t[1] not in temp:
                temp[t[1]] = dict({"id": t[1]})
            temp[t[1]][traveler_info_key] = data.get(key)
    travelers = []

    for tId in temp:
        form = TravelerInfoForm(temp[tId])
        if form.is_valid():
            travelers.append(
                {
                    "index": form.cleaned_data["id"],
                    "date_of_birth": form.cleaned_data['dateOfBirth'].isoformat(),
                    "first_name": form.cleaned_data["firstName"], 
                    "last_name": form.cleaned_data['lastName'], 
                    "middle_name": form.cleaned_data['middleName'],
                    "gender": form.cleaned_data.get("gender", MALE),
                    "email_address": form.cleaned_data["emailAddress"],
                    "phone": f"({form.cleaned_data['phoneCountryCode']}) {form.cleaned_data['phoneNumber']}",
                    "country":form.cleaned_data["country"],
                    "passport_number": form.cleaned_data.get("passportNumber", None),
                    "passport_issue_date": form.cleaned_data.get("passportIssueDate", None),
                    "passport_expiry_date": form.cleaned_data.get('passportExpiryDate', None),
                    "passport_country": form.cleaned_data.get('passportCountry', None),
                    "type": form.cleaned_data.get('type', None)
                }
            )
    return travelers
