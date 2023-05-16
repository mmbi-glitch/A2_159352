from . import db
import pendulum as pdl
from datetime import datetime

# ----------- models --------------- #

def icao_to_loc(code):
    match code:
        case "NZNE":
            return "Dairy Flat"
        case "YMHB":
            return "Hobart"
        case "NZRO":
            return "Rotorua"
        case "NZCI":
            return "Chatham Islands"
        case "NZGB":
            return "Great Barrier Island"
        case "NZTL":
            return "Lake Tekapo"

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seats = db.Column(db.Integer)
    origin = db.Column(db.String(200))
    dest = db.Column(db.String(200))
    origin_code = db.Column(db.String(4))
    dest_code = db.Column(db.String(4))
    leave_dt = db.Column(db.TIMESTAMP(timezone=True))
    arrival_dt = db.Column(db.TIMESTAMP(timezone=True))
    operator = db.Column(db.String(200), default="MilkRun Airways")
    aircraft_model = db.Column(db.String(200))
    stopover = db.Column(db.String(200))

    def __init__(self, seats : int, origin_code : str, dest_code : str, leave_dt : pdl.datetime, arrival_dt : pdl.datetime, stopover : str, aircraft_model : str):

        self.seats = seats
        self.origin_code = origin_code
        self.dest_code = dest_code
        self.origin = icao_to_loc(origin_code)
        self.dest = icao_to_loc(dest_code)
        self.leave_dt = leave_dt
        self.arrival_dt = arrival_dt
        self.stopover = icao_to_loc(stopover)
        self.aircraft_model = aircraft_model

    def __repr__(self):
        return f"Flight('ID:{self.id}', 'SEATS:{self.seats}', OUT_DT:'{self.leave_dt}', 'IN_DT:{self.arrival_dt}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_ref = db.Column(db.String(6), unique=True)
    outbound_flight_id = db.Column(db.Integer, db.ForeignKey("flight.id"))
    inbound_flight_id = db.Column(db.Integer, db.ForeignKey("flight.id"))
    outbound_flight = db.relationship("Flight", foreign_keys=[inbound_flight_id])
    inbound_flight = db.relationship("Flight", foreign_keys=[outbound_flight_id])
    def __init__(self, booking_ref, outbound_flight, inbound_flight):
        self.booking_ref = booking_ref
        self.outbound_flight = outbound_flight
        self.inbound_flight = inbound_flight

    def __repr__(self):
        return f"Booking('{self.booking_ref}')"


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    customer_booking_ref = db.Column(db.String(6), db.ForeignKey("booking.booking_ref"))

    def __init__(self, first_name : str, last_name : str, booking_ref : str):
        self.first_name = first_name
        self.last_name = last_name
        self.customer_booking_ref = booking_ref

    def __repr__(self):
        return f"Customer('{self.first_name}', '{self.last_name}', '{self.customer_booking_ref}')"


# ------------- test data (for entirety of 2023) ---------------- #

def get_dates_of_certain_day(start_date : pdl.datetime, certain_day : pdl.constants):
    dates = list()
    date_object = start_date

    if date_object.weekday() != (certain_day - 1) % 7:
        date_object = date_object.next(certain_day)

    while date_object.year == start_date.year:
        dates.append(date_object)
        date_object = date_object.add(days=7)

    return dates

# ------------ outbound flights ------------------ #

outbound_flights = list()

# 1st Service - syberjet plane
outbound_dates = get_dates_of_certain_day(pdl.today("Pacific/Auckland"), pdl.FRIDAY)

for date in outbound_dates:
    # print(date)
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=8, minute=30, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(hours=3, minutes=50)).in_tz("Australia/Hobart")
    outbound_flights.append(Flight(5, "NZNE", "YMHB", outbound_dt, inbound_dt, "NZRO", "SyberJet SJ30i"))

# 2nd service - 1st cirrus plane

outbound_dates.clear()

for day in [pdl.MONDAY, pdl.TUESDAY, pdl.WEDNESDAY, pdl.THURSDAY, pdl.FRIDAY]:
    outbound_dates.extend(get_dates_of_certain_day(pdl.today("Pacific/Auckland"), day))

for date in outbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=7, minute=45, tz="Pacific/Auckland")
    outbound_dt_2 = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=17, minute=15, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(minutes=45))
    outbound_flights.append(Flight(4, "NZNE", "NZRO", outbound_dt, inbound_dt, "", "Cirrus SF50"))
    inbound_dt = (outbound_dt_2.add(minutes=45))
    outbound_flights.append(Flight(4, "NZNE", "NZRO", outbound_dt_2, inbound_dt, "", "Cirrus SF50"))

# 3rd service - 2nd cirrus plane

outbound_dates.clear()

for day in [pdl.MONDAY, pdl.WEDNESDAY, pdl.FRIDAY]:
    outbound_dates.extend(get_dates_of_certain_day(pdl.today("Pacific/Auckland"), day))

for date in outbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=10, minute=45, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(minutes=20))
    outbound_flights.append(Flight(4, "NZNE", "NZGB", outbound_dt, inbound_dt, "", "Cirrus SF50"))

# 4th service - 1st honda jet

outbound_dates.clear()

for day in [pdl.TUESDAY, pdl.FRIDAY]:
    outbound_dates.extend(get_dates_of_certain_day(pdl.today("Pacific/Auckland"), day))

for date in outbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=14, minute=15, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(hours=2, minutes=15))
    outbound_flights.append(Flight(5, "NZNE", "NZCI", outbound_dt, inbound_dt, "", "HondaJet Elite"))

# 5th service - 2nd honda jet

outbound_dates.clear()

outbound_dates = get_dates_of_certain_day(pdl.today("Pacific/Auckland"), pdl.MONDAY)

for date in outbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=16, minute=35, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(hours=3, minutes=10))
    outbound_flights.append(Flight(5, "NZNE", "NZTL", outbound_dt, inbound_dt, "", "HondaJet Elite"))

print("outbound:",len(outbound_flights))

outbound_dates.clear()

# --------------- inbound flights ----------------------- #

inbound_flights = list()

# 1st Service - syberjet plane
inbound_dates = get_dates_of_certain_day(pdl.today("Australia/Hobart"), pdl.SUNDAY)

for date in inbound_dates:
    # print(date)
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=14, minute=15, tz="Australia/Hobart")
    inbound_dt = (outbound_dt.add(hours=3, minutes=50)).in_tz("Pacific/Auckland")
    inbound_flights.append(Flight(5, "YMHB", "NZNE", outbound_dt, inbound_dt, "", "SyberJet SJ30i"))

# 2nd service - 1st cirrus plane

inbound_dates.clear()

for day in [pdl.MONDAY, pdl.TUESDAY, pdl.WEDNESDAY, pdl.THURSDAY, pdl.FRIDAY]:
    inbound_dates.extend(get_dates_of_certain_day(pdl.today("Pacific/Auckland"), day))

for date in inbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=12, tz="Pacific/Auckland")
    outbound_dt_2 = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=20, minute=15, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(minutes=45))
    inbound_flights.append(Flight(4, "NZRO", "NZNE", outbound_dt, inbound_dt, "", "Cirrus SF50"))
    inbound_dt = (outbound_dt_2.add(minutes=45))
    inbound_flights.append(Flight(4, "NZRO", "NZNE", outbound_dt_2, inbound_dt, "", "Cirrus SF50"))

# 3rd service - 2nd cirrus plane

inbound_dates.clear()

for day in [pdl.TUESDAY, pdl.THURSDAY, pdl.SATURDAY]:
    inbound_dates.extend(get_dates_of_certain_day(pdl.today("Pacific/Auckland"), day))

for date in inbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=10, minute=45, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(minutes=20))
    inbound_flights.append(Flight(4, "NZGB", "NZNE", outbound_dt, inbound_dt, "", "Cirrus SF50"))

# 4th service - 1st honda jet

inbound_dates.clear()

for day in [pdl.WEDNESDAY, pdl.SATURDAY]:
    inbound_dates.extend(get_dates_of_certain_day(pdl.today("Pacific/Auckland"), day))

for date in inbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=10, minute=15, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(hours=2, minutes=15))
    inbound_flights.append(Flight(5, "NZCI", "NZNE", outbound_dt, inbound_dt, "", "HondaJet Elite"))

# 5th service - 2nd honda jet

inbound_dates.clear()

inbound_dates = get_dates_of_certain_day(pdl.today("Pacific/Auckland"), pdl.TUESDAY)

for date in outbound_dates:
    outbound_dt = pdl.datetime(year=date.year, month=date.month, day=date.day, hour=17, minute=25, tz="Pacific/Auckland")
    inbound_dt = (outbound_dt.add(hours=3, minutes=10))
    inbound_flights.append(Flight(5, "NZTL", "NZNE", outbound_dt, inbound_dt, "", "HondaJet Elite"))

print("inbound:",len(inbound_flights))

inbound_dates.clear()
flights = outbound_flights + inbound_flights
print("both:", len(flights))

