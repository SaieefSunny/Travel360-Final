from . import db
from flask_login import UserMixin

class Agency(db.Model, UserMixin):
    agency_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    agency_name = db.Column(db.String(250))
    password_hash = db.Column(db.String(255))
    registration_date = db.Column(db.Date)
    last_login_date = db.Column(db.Date)
    phone = db.Column(db.String(50))
    address = db.Column(db.String(250))
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    zip = db.Column(db.String(50))
    dail_code = db.Column(db.String(50))
    currency = db.Column(db.Enum('USD', 'BDT'), nullable=False)
    website = db.Column(db.String(250), unique=True)
    accounts = db.relationship('AgencyAccount', backref='agency', lazy=True)
    customers = db.relationship('Customer', backref='agency', lazy=True)
    owners = db.relationship('AgencyOwners', backref='agency', lazy=True)
    search_history = db.relationship('SearchHistory', backref='agency', lazy=True)
    bookings = db.relationship('Booking', backref='agency', lazy=True)
    
    # Add this function to override get_id
    def get_id(self):
        return self.agency_id 

class AgencyAccount(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.agency_id'), nullable=False)
    balance = db.Column(db.Integer)

class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.agency_id'), nullable=False)
    firstname = db.Column(db.String(250), nullable=False)
    lastname = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(50), default=None, nullable=False)
    birth_date = db.Column(db.String(250), nullable=False)
    dial_code = db.Column(db.String(50), default=None, nullable=False)
    phone = db.Column(db.String(50), default=None, nullable=False)
    email = db.Column(db.String(50), default=None, nullable=False)
    address = db.Column(db.String(250), default=None, nullable=False)
    city = db.Column(db.String(250), default=None, nullable=False)
    state = db.Column(db.String(250), default=None, nullable=False)
    zip = db.Column(db.String(50), default=None, nullable=False)
    passport_num = db.Column(db.String(250), default=None, nullable=False)
    passport_exp_date = db.Column(db.String(250), default=None, nullable=False)
    nid_number = db.Column(db.String(250), default=None, nullable=False)
    
class AgencyOwners(db.Model):
    owner_id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.agency_id'), default=None)
    agency_name = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(50), default=None)
    email = db.Column(db.String(50), default=None)
    address = db.Column(db.String(250), default=None)
    city = db.Column(db.String(250), default=None)
    state = db.Column(db.String(250), default=None)
    zip = db.Column(db.String(50), default=None)

class CustomerDocument(db.Model):
    doc_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=True)
    upload_pass = db.Column(db.String(250), nullable=True)
    upload_visa = db.Column(db.String(250), nullable=True)
    
class Flight(db.Model):
    flight_id = db.Column(db.Integer, primary_key=True)
    airline_id = db.Column(db.Integer, nullable=False)
    departure_city = db.Column(db.String(250), nullable=False)
    arrival_city = db.Column(db.String(250), nullable=False)
    departure_time = db.Column(db.String(250))
    arrival_time = db.Column(db.String(250))
    ticket_price = db.Column(db.Numeric(10, 2))
    seat_availability = db.Column(db.Integer)

class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('agency_account.account_id'), nullable=False)
    payment_date = db.Column(db.String(250), nullable=False)
    payment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.Enum('Pending', 'Completed', 'Canceled'), nullable=False)

class SearchHistory(db.Model):
    search_id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.agency_id'), nullable=False)
    from_location = db.Column(db.String(100)) 
    to_location = db.Column(db.String(100)) 
    search_date_time = db.Column(db.String(250))
    response = db.Column(db.Text, default=None)

class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.agency_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.flight_id'), nullable=False)
    timestamp = db.Column(db.String(250))
    
    
class Airline(db.Model):
    airline_id = db.Column(db.Integer, primary_key=True)
    AirlineCode = db.Column(db.String(250))
    AirlineName = db.Column(db.String(250))
    AlternativeBusinessName = db.Column(db.String(250))

    
class Airport(db.Model):
    airport_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    iata_code = db.Column(db.String(100))
    icao_code = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    country_code = db.Column(db.String(100))
    
    
class Country(db.Model):
    country_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False, unique=True)
    code3 = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(250), nullable=False)
    
    
class Timezone(db.Model):
    timezone_id = db.Column(db.Integer, primary_key=True)
    timezone = db.Column(db.String(100), nullable=False)
    gmt = db.Column(db.String(100), nullable=False)
    dst = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(100), nullable=False)
    
    
class City(db.Model):
    city_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    city_code = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    country_code = db.Column(db.String(100), nullable=False)
    

class Cabin(db.Model):
    cabin_id = db.Column(db.Integer, primary_key=True)
    cabin_code = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(250), nullable=False)
    
    