from flask import Flask
import pymysql
import requests
from datetime import datetime
import os
import time
import pytz

app = Flask(__name__)

malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")
# 🔹 OpenWeather API Setup
CITY = "Kudat"
API_KEY = os.environ['API_KEY']
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# 🔹 MySQL Database Connection Details from Secrets
DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']


# 🔹 Function to Fetch and Store Weather Data
def fetch_and_store_weather():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        if "main" not in data or "wind" not in data:
            return "Error: Invalid API response format"

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        timestamp = datetime.now(malaysia_tz).strftime('%Y-%m-%d %H:%M:%S')

        connection = pymysql.connect(host=DB_HOST,
                                     user=DB_USER,
                                     password=DB_PASSWORD,
                                     database=DB_NAME)
        cursor = connection.cursor()

        insert_query = "INSERT INTO weather_data (timestamp, temperature, humidity, wind_speed) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (timestamp, temp, humidity, wind_speed))

        connection.commit()
        cursor.close()
        connection.close()

        print(
            f"✅ {timestamp} - Temp: {temp}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s"
        )

    except Exception as e:
        print(f"❌ Error: {e}")


# 🔹 Flask Route to Trigger Data Logging Manually
@app.route("/")
def home():
    try:
        fetch_and_store_weather()
        return "Weather data logged successfully!"
    except Exception as e:
        return f"Error: {str(e)}"


# 🔹 Continuous Loop to Run Every 5 Minutes
if __name__ == "__main__":
    def background_task():
        while True:
            fetch_and_store_weather()
            time.sleep(300)
            
    import threading
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()
    
    app.run(host='0.0.0.0', port=10000)
