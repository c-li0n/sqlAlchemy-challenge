import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask
from flask import jsonify

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#Flask setup
tripapp = Flask(__name__)

@tripapp.route("/")
def home():

    return (
        f"All Available routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"----------------<br/>"
        f"Brant's trip dates:<br/><br/>"
        f"/api/v1.0/2017-04-20/2017-04-30<br/>"
        f"----------------<br/>"
        f"Enter your trip dates in form YYYY-MM-DD:<br/><br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

@tripapp.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').all()

    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_data.append(prcp_dict)
    
    return jsonify(prcp_data)

@tripapp.route("/api/v1.0/stations")
def station():
    session = Session(engine)

    sel = [func.count(Measurement.tobs), Station.station, Station.id ]
    results = session.query(*sel).\
    filter(Measurement.station == Station.station).\
    group_by('station').\
    order_by(func.count(Measurement.tobs).desc()).all()

    station_data = []
    for count, station, station_id in results:
        station_dict = {}
        station_dict['count'] = count
        station_dict['station'] = station
        station_dict['station_id'] = station_id

        station_data.append(station_dict)

    return jsonify(station_data)

@tripapp.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519397').\
    filter(Measurement.date >= '2016-08-23').all()

    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temperature observation'] = tobs
        tobs_data.append(tobs_dict)


    return jsonify(tobs_data)

@tripapp.route("/api/v1.0/<start>")

def start_date(start):

    session = Session(engine)

    def calc_temps(start):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    trip_temps = calc_temps(start)

    for min, avg, max in trip_temps:
        trip_data = {'First day of trip': start}
        trip_data['min temp'] = min
        trip_data['avg temp'] = avg
        trip_data['max temp'] = max

    return jsonify(trip_data)

@tripapp.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    session = Session(engine)

    def calc_temps(start_date, end_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    trip_temps = calc_temps(start, end)

    for min, avg, max in trip_temps:
        trip_data = {'First day of trip': start, 'Last day of trip': end}
        trip_data['min temp'] = min
        trip_data['avg temp'] = avg
        trip_data['max temp'] = max
        

    return jsonify(trip_data)


if __name__ == '__main__':
    tripapp.run(debug=True)