from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Agency, Customer, SearchHistory, Country, Airport, City, Airline, Cabin
from . import db
import requests
import json
from datetime import datetime, timedelta
import pytz

from cryptography.fernet import Fernet
from collections import defaultdict
views = Blueprint('views', __name__)


# Secret key for encryption and decryption
SECRET_KEY = "your_secret_key_here"


@views.route('/get_airport_suggestions', methods=['GET'])
def get_airport_suggestions():
    search = request.args.get('search', '').strip().lower()
    page = int(request.args.get('page', 1))  
    per_page = 50 
    
    offset = (page - 1) * per_page
    
    airports = db.session.query(Airport, Country.name).join(
        Country, Airport.country_code == Country.code
    ).filter(
        db.or_(
            Airport.name.ilike(f'%{search}%') 
            #Airport.iata_code.ilike(f'%{search}'), 
            #Country.name.ilike(f'%{search}%')
        )
    ).limit(per_page).offset(offset).all()

    airport_suggestions = [{'name': airport.name, 'iata_code': airport.iata_code, 'country_name': country_name}
                           for airport, country_name in airports]
    print(airport_suggestions)
    return jsonify({'airports': airport_suggestions})


def convert_and_format_time(raw_time):
    user_timezone_offset =6
    
    time_parts = raw_time.split('+') if '+' in raw_time else raw_time.split('-')
    if len(time_parts) != 2:
        raise ValueError("Invalid time format")

    time_str = time_parts[0]
    sign = '+' if '+' in raw_time else '-'
    offset_str = time_parts[1]

    parsed_time = datetime.strptime(time_str, '%H:%M:%S')

    offset_hours = int(offset_str.split(':')[0])
    offset_minutes = int(offset_str.split(':')[1])

    if sign == '+':
        user_offset_minutes = user_timezone_offset * 60
        offset_difference_minutes = user_offset_minutes - (offset_hours * 60 + offset_minutes)
    elif sign == '-':
        user_offset_minutes = user_timezone_offset * 60
        offset_difference_minutes = user_offset_minutes + (offset_hours * 60 + offset_minutes)
    else:
        raise ValueError("Invalid sign in the offset")


    adjusted_time = parsed_time + timedelta(minutes=offset_difference_minutes)
    formatted_time = adjusted_time.strftime('%I:%M %p')

    return formatted_time

def get_airport_name(departure_airport_iata):
    departure_airport = Airport.query.filter_by(iata_code=departure_airport_iata).first()
    departure_airport_name = departure_airport.name if departure_airport else departure_airport_iata
    return departure_airport_name

def get_city_name(departure_city_iata):
    departure_city = City.query.filter_by(city_code=departure_city_iata).first()
    departure_city_name = departure_city.name if departure_city else departure_city_iata
    return departure_city_name

def get_country_name(departure_country_code):
    departure_country = Country.query.filter_by(code=departure_country_code).first()
    departure_country_name = departure_country.name if departure_country else departure_country_code

    return departure_country_name

def format_date(input_date):
    
    parsed_date = datetime.strptime(input_date, '%Y-%m-%d')
    formatted_date = parsed_date.strftime('%a, %d %b %y')

    return formatted_date

def convert_duration(minutes):
    if minutes < 0:
        raise ValueError("Duration cannot be negative")

    days = minutes // 1440
    hours = (minutes % 1440) // 60
    minutes = minutes % 60

    duration_str = ""

    if days > 0:
        duration_str += f"{days} day{'s' if days > 1 else ''}, "

    if hours > 0:
        duration_str += f"{hours} hour{'s' if hours > 1 else ''}, "

    if minutes > 0:
        duration_str += f"{minutes} minute{'s' if minutes > 1 else ''}"

    if duration_str.endswith(", "):
        duration_str = duration_str[:-2]

    return duration_str

def get_airline_name(airline_code):
    airline = Airline.query.filter_by(AirlineCode=airline_code).first()
    if airline:
        return airline.AlternativeBusinessName
    else:
        return None

def get_cabin_name(cabin_code):
    cabin = Cabin.query.filter_by(cabin_code=cabin_code).first()
    if cabin:
        return cabin.name
    else:
        return None



key = Fernet.generate_key()

def encrypt(text):
    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(text.encode())
    return encrypted_text

def decrypt(encrypted_text):
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(encrypted_text)
    return decrypted_text.decode()


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/viewprofile')
@login_required
def viewprofile():
    return render_template("viewprofile.html", user=current_user)


@views.route('/view_flight/<int:search_id>', methods=['GET'])
@login_required
def view_flight(search_id):
    search_history = SearchHistory.query.filter_by(search_id=search_id, agency_id=current_user.agency_id).first()
    if search_history:
        flight_schedules = json.loads(search_history.response)
        flight_count = len(flight_schedules)
        return render_template('flights.html', flight_schedules=flight_schedules, flight_count=flight_count)
    else:
        error_message = "Search history not found."
        return render_template('flights.html', error_message=error_message)
    

@views.route('/flights', methods=['GET', 'POST'])
@login_required
def flights():
    if request.method == 'POST':
        iata_from = request.form.get('iataFrom')
        iata_to = request.form.get('iataTo')
        journey_date = request.form.get('journey_date')
        adult = request.form.get('adult')
        child = request.form.get('child')
        infant = request.form.get('infant')
        cabin = request.form.get('select_cabin')

        print( adult, child, infant, cabin)
        sabre_api_url = f'https://api.cert.platform.sabre.com/v4/offers/shop'

        headers = {
            "Authorization": f"Bearer T1RLAQJl7PCx+uMQW4bTBqGf3quNgeakNF5yZLQApxWMsbqqkRB5YZDJs8L3gvh4klQQ78VyAADgpra6XonPFWIBBBf23IG7pMF3OrOhEwnlkLg3GUiDsNrw4KeRkgpai/kFp+wDBPkwzge9pHlFn2DDd7eDrZ7HCR6E27NA5lItrZwsFZvQsv02YTeMfW64rYpWiB2sss7PQSo5s1up63qojb+DeWF3lYIEc6TEKC04W1qSf18V/T5g6NmmFh4WTxIG0vpLTLJsGbU+5fVOT0ZuZ/wgqw+impb5kjBj+kkQf4RRr3saLbCnn2lUjMZrIuJNEgjTDsnIY6ceHZ5GRp2aRIaHo6AoflpDOkAjHqKfQYtkxHcUHq8*"
        }

        request_body = {
            "OTA_AirLowFareSearchRQ": {
                "ResponseType": "GIR",
                "Version": "4",
                "AvailableFlightsOnly": True,
                "POS": {
                    "Source": [
                        {
                            "PseudoCityCode": "40OK",
                            "RequestorID": {
                                "Type": "1",
                                "ID": "1",
                                "CompanyName": {
                                    "Code": "TN"
                                }
                            }
                        }
                    ]
                },
                "OriginDestinationInformation": [
                    {
                        "RPH": "1",
                        "DepartureDateTime": journey_date+"T00:00:00",
                        "OriginLocation": {
                            "LocationCode": iata_from
                        },
                        "DestinationLocation": {
                            "LocationCode": iata_to
                        }
                    }
                ],
                "TravelerInfoSummary": {
                    "AirTravelerAvail": [
                        {
                            "PassengerTypeQuantity": [
                                {
                                    "Code": "ADT",
                                    "Quantity": 1
                                }
                            ]
                        }
                    ]
                },
                "TPA_Extensions": {
                    "IntelliSellTransaction": {
                        "RequestType": {
                            "Name": "50ITINS"
                        }
                    }
                }
            }
        }


        try:

            response = requests.post(sabre_api_url, headers=headers, json=request_body)
            response.raise_for_status()

            response_data = response.json()

            messages = response_data["groupedItineraryResponse"]["messages"]
            statistics = response_data["groupedItineraryResponse"]["statistics"]
            schedule_descs = response_data["groupedItineraryResponse"]["scheduleDescs"]
            tax_descs = response_data["groupedItineraryResponse"]["taxDescs"]
            tax_summary_descs = response_data["groupedItineraryResponse"]["taxSummaryDescs"]
            fare_component_descs = response_data["groupedItineraryResponse"]["fareComponentDescs"]
            baggage_allowance_descs = response_data["groupedItineraryResponse"]["baggageAllowanceDescs"]
            leg_descs = response_data["groupedItineraryResponse"]["legDescs"]
            itinerary_groups = response_data["groupedItineraryResponse"]["itineraryGroups"]

            departure_date = response_data["groupedItineraryResponse"]["itineraryGroups"][0]["groupDescription"]["legDescriptions"][0]["departureDate"]
            itineraries = [group["itineraries"] for group in itinerary_groups]
            leg_mapping = {leg_desc["id"]: leg_desc for leg_desc in leg_descs}
            tax_mapping = {tax_desc["id"]: tax_desc for tax_desc in tax_descs}
            tax_summary_mapping = {tax_summary_desc["id"]: tax_summary_desc for tax_summary_desc in tax_summary_descs}
            schedule_mapping = {schedule_desc["id"]: schedule_desc for schedule_desc in schedule_descs}
            baggage_allowance_mapping = {allowance_desc["id"]: allowance_desc for allowance_desc in baggage_allowance_descs}

            for itinerary_group in itineraries:
                for itinerary in itinerary_group:
                    
                    for leg in itinerary["legs"]:
                        
                        ref = leg["ref"]                    
                        leg_desc = leg_mapping.get(ref)
                        if leg_desc:
                            leg["ref"] = leg_desc

                        for schedule_ref in leg["ref"]["schedules"]:
                            schedule_desc = schedule_mapping.get(schedule_ref["ref"])
                            if schedule_desc:
                                schedule_ref["ref"] = schedule_desc
                    
                    for pricing_info in itinerary["pricingInformation"]:
                        taxes = pricing_info["fare"]["passengerInfoList"][0]["passengerInfo"]["taxes"]
                        updated_taxes = [tax_mapping[tax["ref"]] for tax in taxes]
                        pricing_info["fare"]["passengerInfoList"][0]["passengerInfo"]["taxes"] = updated_taxes

                    for pricing_info in itinerary["pricingInformation"]:
                        tax_summaries = pricing_info["fare"]["passengerInfoList"][0]["passengerInfo"]["taxSummaries"]
                        updated_tax_summaries = [tax_summary_mapping[tax_summary["ref"]] for tax_summary in tax_summaries]
                        pricing_info["fare"]["passengerInfoList"][0]["passengerInfo"]["taxSummaries"] = updated_tax_summaries

                    stops = sum([len(leg["ref"]["schedules"]) - 1 for leg in itinerary["legs"]])

                    
                    leg["stops"] = stops
                    itinerary["stops"] = stops
                    
                    for pricing_info in itinerary["pricingInformation"]:
                        passenger_info = pricing_info["fare"]["passengerInfoList"][0]["passengerInfo"]
                        baggage_info = passenger_info.get("baggageInformation")

                        if baggage_info:
                            updated_baggage_info = []

                            for baggage_item in baggage_info:
                                allowance_ref = baggage_item.get("allowance", {}).get("ref")
                                allowance_desc = baggage_allowance_mapping.get(allowance_ref)

                                if allowance_desc:
                                    baggage_item["allowance"] = allowance_desc
                                    updated_baggage_info.append(baggage_item)

                            passenger_info["baggageInformation"] = updated_baggage_info
            
            #print("Updated Itineraries:", itineraries)
            
            airline_frequencies = defaultdict(int)
            for group in itinerary_groups:
                for itinerary in group['itineraries']:
                    for pricing_info in itinerary['pricingInformation']:
                        if 'baggageInformation' in pricing_info['fare']['passengerInfoList'][0]['passengerInfo']:
                            airline_code = pricing_info['fare']['passengerInfoList'][0]['passengerInfo']['baggageInformation'][0]['airlineCode']
                            airline_frequencies[airline_code] += 1
            
            
            cabin_code_frequencies = defaultdict(int)

            for group in itinerary_groups:
                for itinerary in group['itineraries']:
                    counted_cabin = False
                    for pricing_info in itinerary['pricingInformation']:
                        for passenger_info in pricing_info['fare']['passengerInfoList']:
                            for fare_component in passenger_info['passengerInfo']['fareComponents']:
                                for segment in fare_component['segments']:
                                    cabin_code = segment['segment']['cabinCode']
                                    if not counted_cabin:
                                        cabin_code_frequencies[cabin_code] += 1
                                        counted_cabin = True



            return render_template('flights.html', itineraries=itineraries, statistics= statistics["itineraryCount"], departure_date=departure_date, timedelta=timedelta,
                                convert_and_format_time=convert_and_format_time,
                                get_airport_name=get_airport_name,
                                get_city_name=get_city_name,
                                get_country_name=get_country_name,
                                format_date=format_date,
                                convert_duration=convert_duration,
                                get_airline_name=get_airline_name,
                                get_cabin_name=get_cabin_name,
                                airline_frequencies=airline_frequencies,
                                cabin_code_frequencies=cabin_code_frequencies,
                                encrypt=encrypt, decrypt=decrypt
                                )

        except Exception as e:
            error_message = str(e)
            print(f"Error: {error_message}")


    return render_template("flights.html", user=current_user)




# @views.route('/search_history')
# @login_required
# def search_history():
#     search_history = SearchHistory.query.all()
#     return render_template("search_history.html", user=current_user, search_history=search_history)



@views.route('/flightshistory')
@login_required
def flightshistory():
    return render_template("flightshistory.html", user=current_user)



@views.route('/flightitinerary')
@login_required
def flightitinerary():

    flight = request.args.get('flight')
    

    return render_template("flightitinerary.html", user=current_user)



@views.route('/hotels')
@login_required
def hotels():
    return render_template("hotels.html", user=current_user)

@views.route('/hotelshistory')
@login_required
def hotelshistory():
    return render_template("hotelshistory.html", user=current_user)


@views.route('/hotelsbookingserach')
@login_required
def hotelsbookingserach():
    return render_template("hotelsbookingserach.html", user=current_user)


@views.route('/flightsbookinghistory')
@login_required
def flightsbookinghistory():
    return render_template("flightsbookinghistory.html", user=current_user)


@views.route('/clients')
@login_required
def clients():
    customers = Customer.query.all()
    return render_template("clients.html", user=current_user, customers=customers)



@views.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    
    if request.method == 'POST':
        agency_id = current_user.agency_id
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        dial_code = request.form.get('dial_code')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip = request.form.get('zip')
        passport_num = request.form.get('passport_num')
        passport_exp_date = request.form.get('passport_exp_date')
        nid_number = request.form.get('nid_number')
        
        nid = Customer.query.filter_by(nid_number=nid_number).first() 
        passport = Customer.query.filter_by(passport_num=passport_num).first() 
        
        if nid:
            flash('Duplicate NID Entry', category='error')

        elif passport:
            flash('Duplicate Passport Entry', category='error')
        else:
            new_customer = Customer(
                agency_id=agency_id,
                firstname=firstname,
                lastname=lastname,
                gender=gender,
                birth_date=birth_date,
                dial_code=dial_code,
                phone=phone,
                email=email,
                address=address,
                city=city,
                state=state,
                zip=zip,
                passport_num=passport_num,
                passport_exp_date=passport_exp_date,
                nid_number=nid_number
            )
        
            db.session.add(new_customer)
            db.session.commit()
                
            flash('Customer added successfully', category='success')
        
    return render_template("add_client.html", user=current_user)


@views.route('/wallet')
@login_required
def wallet():
    return render_template("mywallet.html", user=current_user)