# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from flask import request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/startend<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    one_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    scores = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_date).all()
    session.close()

    precipitation_list = list(np.ravel(scores))
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    all_stations = session.query(station.station).all()
    session.close()

    stations_list = list(np.ravel(all_stations))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    one_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_data = session.query(measurement.tobs).filter(measurement.station == 'USC00519281', measurement.date >= one_year_date).all()
    session.close()

    temp_list = list(np.ravel(temp_data))
    return jsonify(temp_list)

@app.route("/api/v1.0/start")
def start():
    start_date = request.args.get('start')
    
    if start_date:
        session = Session(engine)
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
        
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).all()
        
        session.close()

        temperature_start_date = [{"MIN": result[0], "AVG": result[1], "MAX": result[2]} for result in results]

        return jsonify({"start_date": start_date.strftime('%Y-%m-%d'), "temperature_data": temperature_start_date})
    
    else:
        return jsonify({"error": "Provide a start date in the format 'YYYY-MM-DD' in the URL. ex. http://(input local host)/api/v1.0/start?start=2017-08-23"})

@app.route("/api/v1.0/startend")
def startend():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if start_date and end_date:
        session = Session(engine)
        
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date, measurement.date <= end_date).all()
        
        session.close()

        temperature_data = [{"MIN": result[0], "AVG": result[1], "MAX": result[2]} for result in results]

        return jsonify({"start_date": start_date.strftime('%Y-%m-%d'), "end_date": end_date.strftime('%Y-%m-%d'), "temperature_data": temperature_data})
    
    else:
        return jsonify({"error": "Provide start and end dates in the format 'YYYY-MM-DD' in the URL. ex. http://(input local host)/api/v1.0/startend?start=2017-08-23&end=2017-08-24"})

if __name__ == '__main__':
    app.run(debug=True)