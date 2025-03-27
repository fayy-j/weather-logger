import requests

PHP_URL = "http://kb-weather.kesug.com/insert.php"

test_payload = {
    "timestamp": "2025-03-28 12:00:00",
    "temperature": 30.5,
    "humidity": 80,
    "wind_speed": 5.6
}

response = requests.post(PHP_URL, json=test_payload)
print("Response from PHP:", response.text)
