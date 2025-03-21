import pymysql
import requests
from datetime import datetime
import pytz

# Set Malaysia Timezone
malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")

# OpenWeather API
CITY = "Kudat"
API_KEY = "your_api_key"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# MySQL Database
DB_HOST = "your_db_host"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME = "your_db_name"

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

# Run the function once
fetch_and_store_weather()
