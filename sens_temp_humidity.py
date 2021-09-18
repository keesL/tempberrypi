import Adafruit_DHT
import datetime

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        now=datetime.datetime.now()
        print(f"Now={now}  Temp={temperature}  Humidity={humidity}")
        break
    else:
        print("Failed to retrieve data from humidity sensor")

