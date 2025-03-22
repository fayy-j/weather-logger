import pymysql
import requests
from datetime import datetime
import pytz
import os
import time
from flask import Flask

app = Flask(__name__)

# Set Malaysia Timezone
malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")

# OpenWeather API
CITY = "Kudat"
API_KEY = os.getenv('API_KEY')
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# MySQL Database
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def fetch_and_store_weather():
    try:
        response = requests.get(URL)
        data = response.json()

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        timestamp = datetime.now(malaysia_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Connect to MySQL
        connection = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cursor = connection.cursor()

        insert_query = "INSERT INTO weather_data (timestamp, temperature, humidity, wind_speed) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (timestamp, temp, humidity, wind_speed))

        connection.commit()
        cursor.close()
        connection.close()

        print(f"✅ {timestamp} - Temp: {temp}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s")

    except Exception as e:
        print("❌ Error:", e)

# Schedule the function to run every 10 minutes
def run_scheduler():
    while True:
        fetch_and_store_weather()
        time.sleep(10)  # Sleep for 10 minutes

@app.route("/")
def home():
    return "Weather data updating service is running!"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_scheduler).start()
    app.run(host="0.0.0.0", port=10000)
