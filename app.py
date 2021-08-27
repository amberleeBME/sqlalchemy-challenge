import numpy as np
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
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
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

# Define what to do when a user hits the /precipitation route
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results=session.query(Station.station).all()
    session.close()

    # Convert list of tuples into dictionary
    stations_ls=list(np.ravel(results))
    
    return jsonify(stations_ls)

if __name__ == "__main__":
    app.run(debug=True)