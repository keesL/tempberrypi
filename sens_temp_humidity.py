import Adafruit_DHT
import datetime
import requests

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
URL = 'https://www.leune.org/adelphibot/temp.php'

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        now=datetime.datetime.now()
        r = requests.get(URL, params={'temp': temperature, 
            'humidity': humidity,
            'timestamp': now})

        break
    else:
        print("Failed to retrieve data from humidity sensor")

