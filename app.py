from flask import Flask, render_template, redirect, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import plotly.express as px
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from sqlalchemy import inspect

Base = declarative_base()
class SensorData(Base):
    __tablename__ = 'sensor_data'
    id = Column(Integer, primary_key=True)
    devId = Column(String(50))
    value = Column(Float)
    time = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.value

engine = create_engine('sqlite:///sensors.sqlite')
if not inspect(engine).has_table('sensor_data'):
    Base.metadata.create_all(engine)
else:
    print('table exists')
app = Flask(__name__)

def getdb():
    db = scoped_session(sessionmaker(bind=engine))
    return db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sensor')
def sensor():
    # get devid from get request
    devId = request.args.get('devId')
    # get data from db
    try:
        db = getdb()
        data = db.query(SensorData).filter(SensorData.devId == devId).all()
        # check length of data
        if len(data) == 0:
            return render_template('sensor.html', plot="<p class='text-center alert alert-warning'>Nothing to plot</p>")
        # create dataframe
        df = pd.DataFrame()
        df['time'] = [d.time for d in data]
        df['value'] = [d.value for d in data]
        # create plot
        fig = px.line(df, x='time', y='value')
        fig.update_xaxes(rangeslider_visible=True)
        return render_template('sensor.html', plot=fig.to_html())
    except Exception as e:
        print(e)
        return render_template('sensor.html', plot="<p class='text-center alert alert-warning'>Nothing to plot</p>")

@app.route('/sensor/add/<int:devId>', methods=['POST'])
def add_sensor(devId):
    # get value from post request
    value = request.form.get('value')
    # save to db
    db = getdb()
    db.add(SensorData(devId=devId, value=value))
    db.commit()
    # return success response
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
 