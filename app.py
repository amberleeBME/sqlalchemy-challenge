import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Station=Base.classes.station
Measurement=Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# Define what to do when a user hits the index route
@app.route("/")
def home():
    # outputs to terminal/gitbash
    print("Server received request for 'Home' page...")
    # outputs to clientpython
    return (
        f"Welcome to the Climate App!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;YYYY-MM-DD><br/>"
        f"/api/v1.0/&lt;YYYY-MM-DD>/&lt;YYYY-MM-DD><br/>"
    )

# Define what to do when a user hits the /precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation values for the last year in the database
    last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date=dt.strptime(last,'%Y-%m-%d')
    year_ago=latest_date - timedelta(days=365)
    results=session.query(Measurement.date, Measurement.prcp).filter(func.strftime("%Y-%m-%d",Measurement.date)>year_ago).all()
    session.close()

    # Convert list of tuples into dictionary
    precip=dict(results)

    return jsonify(precip)

# Define what to do when a user hits the /stations route
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results=session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    stations_ls=list(np.ravel(results))
    
    return jsonify(stations_ls)

# Define what to do when a user hits the /tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Tobs' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperatures of the most active station for the last year of data
    last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date=dt.strptime(last,'%Y-%m-%d')
    year_ago=latest_date - timedelta(days=365)
    sel=[Measurement.station, Measurement.tobs]
    station_active=session.query(*sel).all()
    df=pd.DataFrame(station_active,columns=['Station','tobs']).groupby('Station').count().sort_values(by='tobs',ascending=False)
    active_id=(df.first_valid_index())
    sel=[Measurement.date, Measurement.tobs]
    results=session.query(*sel).filter(Measurement.station==active_id, func.strftime("%Y-%m-%d",Measurement.date)>year_ago).all()
    
    session.close()

    # Convert list of tuples into dictionary
    active_station=dict(results)

    return jsonify(active_station)
@app.route("/api/v1.0/<start>")
def start(start_date):
    print("Server received request for 'Start' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    print(start_date)
    format_date=dt.strptime(str(start_date),'%Y-%m-%d')
    sel=[Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    results=session.query(*sel).filter(func.strftime("%Y-%m-%d",Measurement.date)==format_date).all()
    session.close()
    start_dict=dict(results)
    return jsonify(start_dict)

if __name__ == "__main__":
    app.run(debug=True)