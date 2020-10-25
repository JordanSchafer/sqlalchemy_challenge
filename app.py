#Import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#Setup database connection
engine =create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#Setup Flask
app=Flask(__name__)

#Setup home route
@app.route("/")
def home():
    return (f"<pre>              Available Routes:<br/><br/>\
              Precipitation:                                     /api/v1.0/precipitation<br/><br/>\
              List of Stations:                                  /api/v1.0/stations<br/><br/>\
              Temperature Observations for last year:            /api/v1.0/tobs<br/><br/>\
              Temperature stats starting at single date:         /api/v1.0/yyyy-mm-dd<br/><br/>\
              Temperature stats for a range of dates:            /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/></pre>")

#Setup precip route
@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
    
    query_data=session.query(Measurement.date,Measurement.prcp).\
               order_by(Measurement.date).all()
    
    precip_dict={}
    
    for date,prcp in query_data:
        precip_dict[date]=prcp
    session.close()
    return jsonify(precip_dict)

#setup station list route
@app.route("/api/v1.0/stations")
def station():
    session=Session(engine)
    stations_querry=session.query(Station.station,Station.name).all()
    stations = {}
    for s,n in stations_querry:
        stations[s]=n
    return jsonify(stations)
 

#setup tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    
    last_date = session.query(Measurement.date).\
                order_by(Measurement.date.desc()).\
                first().date
                
    last_date=dt.datetime.strptime(last_date, "%Y-%m-%d")
    query_date = (last_date - dt.timedelta(days=365)).strftime("%Y-%m-%d")
    
    active_station= session.query(Measurement.station).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).first()
    most_active=active_station[0]
    
    query_data=session.query(Measurement.date,Measurement.tobs).\
               filter(Measurement.date >= query_date).\
               filter(Measurement.station == most_active).all()
               
    year_tobs ={}
    for d,t in query_data:
        year_tobs[d]=t
        
    return jsonify(year_tobs)

#setup temp stats one date
@app.route("/api/v1.0/<start>")
def temp_range_one(start):
    session=Session(engine)
    query_data=session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all()
    
    temp_range={}
    for date,mint,avgt,maxt in query_data:
        temp_range[date]={"min":mint,"avg":avgt,"max":maxt}
    
    return jsonify(temp_range)

#setup temp stats for two dates
@app.route("/api/v1.0/<start>/<end>")
def temp_range_two(start,end):
    session=Session(engine)
    query_data=session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all()
    
    temp_range={}
    for date,mint,avgt,maxt in query_data:
        temp_range[date]={"min":mint,"avg":avgt,"max":maxt}
    
    return jsonify(temp_range)
if __name__ == "__main__":
     app.run(debug=True)
   