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

# PHP API URL (Replace with your InfinityFree URL)
PHP_URL = "http://kb-weather.kesug.com/insert.php"  # Change to your actual URL

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

        # Send data to PHP script
        payload = {
            "timestamp": timestamp,
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed
        }

        php_response = requests.post(PHP_URL, json=payload)  # Use 'json' instead of 'data'
        print(f"✅ {timestamp} - Temp: {temp}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s")
        print("Server response:", php_response.text)

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
