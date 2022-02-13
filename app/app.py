from flask import Flask, render_template 
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os 
# from prediction import predict

import joblib 

def predict(user_inputs):
    # load model binaries 
    model = joblib.load("static/py/model.sav")
    encoder = joblib.load("static/py/encoder.sav")
    X_scaler = joblib.load("static/py/x_scaler.sav")
    y_scaler  = joblib.load("static/py/y_scaler.sav")

    # get the user input data 
    pressure = user_inputs["pressure"]
    humidity = user_inputs["humidity"]
    city_name = user_inputs["city_name"]
    
    # store city names into a df 
    city_input_df = pd.DataFrame({
        "city_name": [city_name]
    })

    # use encoder to transform the city df 
    X_transformed = encoder.transform(city_input_df)
    city_df = pd.DataFrame(columns=[*encoder.categories_], data=X_transformed.toarray())
    
    # store pressure and humidty into df 
    input_df = pd.DataFrame({
        "pressure": [pressure],
        "humidity": [humidity]
    })

    # combine both df's using indexes 
    df = input_df.merge(city_df, left_index=True, right_index=True)

    # scale the X input df 
    X_scaled = X_scaler.transform(df)

    # obtain prediction (y) 
    prediction_scaled = model.predict(X_scaled)
    
    # scale prediction to human readable terms i.e. celcius 
    prediction = y_scaler.inverse_transform(prediction_scaled)
    return prediction[0][0]

# create app 
app = Flask(__name__)

# create database engine 
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SERVER_NAME = os.environ.get("DB_SERVER_NAME")
DB_DATABASE_NAME = os.environ.get("DB_DATABASE_NAME")

connection_url = URL.create(
    drivername = "postgresql+pg8000", 
    username = DB_USER,
    password = DB_PASSWORD,
    host = DB_SERVER_NAME, 
    port = 5432,
    database = DB_DATABASE_NAME, 
)

engine = create_engine(connection_url)

# page routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forecast")
def forecast():
    return render_template("forecast.html")

# API routes 

@app.route("/api/temperature")
def get_temperature():
    recent_temps = pd.read_sql(f"""
        select * 
        from 
            temperature inner join city on temperature.city_id = city.city_id
        where
            name = 'Perth'
        order by datetime desc limit 100
    """, engine)
    return {"temps": recent_temps.to_dict(orient="records")}


@app.route("/api/predict/<pressure>/<humidity>/<city>", methods=["GET"])
def do_predict(pressure, humidity, city):
    user_input = {
        "pressure": float(pressure), 
        "humidity": float(humidity), 
        "city_name": city
    }
    prediction = predict(user_input)

    return {"prediction": prediction}

if __name__ == "__main__":
    app.run(debug=True)
