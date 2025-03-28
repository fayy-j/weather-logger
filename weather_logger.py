import psycopg2
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
CITY = "Kota Belud"
API_KEY = os.environ.get('API_KEY')
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# PostgreSQL Database Credentials
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT', 5432)  # Default PostgreSQL Port

def fetch_and_store_weather():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        
        data = response.json()

        if "main" not in data or "wind" not in data:
            return "Error: Invalid API response format"

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        timestamp = datetime.now(malaysia_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode="require"  # Required for Render
        )
        cursor = connection.cursor()

        # Insert Data
        insert_query = """
        INSERT INTO weather_data (timestamp, temperature, humidity, wind_speed) 
        VALUES (%s, %s, %s, %s)
        """
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
        time.sleep(600)  # Sleep for 10 minutes

@app.route("/")
def home():
    return "Weather data updating service is running!"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_scheduler).start()
    app.run(host="0.0.0.0", port=10000)
