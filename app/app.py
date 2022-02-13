from flask import Flask, render_template 
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os 
import joblib 

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

@app.route("/")
def index():
    return render_template("index.html")

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

if __name__ == "__main__":
    app.run(debug=True)
