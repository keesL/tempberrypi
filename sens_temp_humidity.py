import Adafruit_DHT
import datetime
import requests
import smtplib
import sys
from enum import Enum
from datetime import datetime
from datetime import timedelta

if len(sys.argv) < 2:
    me=sys.argv[0]
    print(f"Invoke this program as {me} <local IP address>.")
    sys.exit(-1)

# global configs
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
URL = 'https://www.leune.org/adelphibot/temp.php'
MAX_TEMP = 26.67 # 80F in Celcius
MAIL_RELAY = ""
MAIL_FRM = ""
MAIL_TO = ""

# helpers

class TempState(Enum):
    ABOVE = 1
    BELOW = 2

class NoticeState(Enum):
    NOTIFIED = 1
    NOT_NOTIFIED = 2

def stateToName(state):
    if state == TempState.ABOVE: return "ABOVE"
    if state == TempState.BELOW: return "BELOW"


def notify(tempState, triggerTime, currentTemp):
    currentTemp = 32 + 9.0/5.0*currentTemp
    with smtplib.SMTP(MAIL_RELAY) as smtpObj:
        smtpObj.sendmail(from_addr=MAIL_FRM, to_addrs=MAIL_TO,
            msg="""From: Tempberry Pi <noreply@example.com>
To: "Email trigger recipients" <noreply@example.com>
Subject: EMAIL TRIGGER """+stateToName(tempState)+"""

Temperature alarm triggered at """+str(triggerTime)+""" local time.

The temperature is """+stateToName(tempState)+""" the maximum temperature.

The current temperature is """+str(round(currentTemp, 1))+""" degrees F.
""")
        smtpObj.quit()
        print("Email sent.")


while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        now=datetime.now()
        r = requests.get(URL, params={'temp': temperature, 
            'humidity': humidity,
            'timestamp': now,
            'addr': sys.argv[1]})

        with open('sensor.log', 'a') as f:
            f.write(f'{now},{temperature},{humidity}\n')
        break
    else:
        print("Failed to retrieve data from humidity sensor")

# retrieve previous state
try:
    with open("state.log", "r") as f:
        data=f.read()
        last_transition,notice_state,temp_state = data.split(",")
except:
    temp_state=TempState.BELOW
    notice_state=NoticeState.NOT_NOTIFIED
    last_transition = datetime(2024,6,20,9,46,0)

# did we trigger a state transition?
if temperature > MAX_TEMP and temp_state == TempState.BELOW:
    temp_state = TempState.ABOVE
    notice_state = NoticeState.NOT_NOTIFIED
elif temperature <= MAX_TEMP and temp_state == TempState.ABOVE:
    temp_state = TempState.BELOW
    notice_state = NoticeState.NOT_NOTIFIED

# do we need to notify and update?
if notice_state == NoticeState.NOT_NOTIFIED:
    if temp_state == TempState.ABOVE: 
        state_name = "above" 
    else: 
        state_name = "below"
    if now - last_transition > timedelta(minutes = 10):
        with open("transition.log", "a") as f:
            f.write(f'{now} Temperature at {temperature}. Transitioning to new state {state_name}\n')
            notify(temp_state, last_transition, temperature)

        notice_state = NoticeState.NOTIFIED
        last_transition = now
    else:
        with open("transition.log", "a") as f:
            f.write(f'{now} Temperature at {temperature}. Too soon to transition to new state {state_name}. Last at {last_transition}\n')
            notify(temp_state, last_transition, temperature)

# update our log
with open("state.log", "w") as f:
    f.write(f"{last_transition},{notice_state},{temp_state}");
