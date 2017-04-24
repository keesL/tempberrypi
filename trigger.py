#!/usr/bin/python
import pickle
import smtplib
from datetime import datetime, timedelta
#############################################
# permissable states:
# - cold
# - normal
# - high
#
# State transitions
# cold --> normal       Email "All good"
# normal --> cold       Email "Temp too low"
# normal --> high       Email "Temp too high"
# high --> normal       Email "Temp ok"
#
# No more than one email per hour

class TempState(object):
    NORMAL = 1
    COLD = 2
    HIGH = 3
    VERYHIGH = 4

    STATENAME = {
            1: 'Normal',
            2: 'Cold',
            3: 'High',
            4: 'VERY HIGH'
    }

    ENVFROM = 'tempberry@example.com'
    RECIPIENTS = [ 'user@example.com', 'user2@example.com' ]

    def __init__(self, filename):
        self.lastNotify = None
        self.saveFile = filename
        try:
            f = open(filename, 'r')
            self.prevState, self.lastNotify = pickle.load(f)
            f.close()
        except:
            self.prevState = TempState.HIGH


    def trigger(self, newState, newTemp):
        if self.prevState == TempState.NORMAL and newState == TempState.COLD:
            self.notify(TempState.COLD, newTemp)
            self.prevState = TempState.COLD

        elif self.prevState == TempState.NORMAL and newState == TempState.HIGH:
            self.notify(TempState.HIGH, newTemp)
            self.prevState = TempState.HIGH

        elif self.prevState == TempState.HIGH and newState == TempState.NORMAL:
            self.notify(TempState.NORMAL, newTemp)
            self.prevState = TempState.NORMAL

        elif self.prevState == TempState.COLD and newState == TempState.NORMAL:
            self.notify(TempState.NORMAL, newTemp)
            self.prevState = TempState.NORMAL

        elif self.prevState == TempState.HIGH and newState == TempState.VERYHIGH:
            self.notify(TempState.VERYHIGH, newTemp)
            self.prevState = TempState.VERYHIGH

        elif self.prevState == TempState.VERYHIGH and newState == TempState.HIGH:
            self.notify(TempState.HIGH, newTemp)
            self.prevState = TempState.HIGH

    
    def notify(self, condition, newTemp):
        now = datetime.now()
        if self.lastNotify is None or now-self.lastNotify > timedelta(hours=2):
            self.lastNotify = now
            with open(self.saveFile, 'w') as f:
                pickle.dump((condition, now), f)
                f.close()
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(TempState.ENVFROM,
                TempState.RECIPIENTS,
                """From: Tempberry Pi <noreply@example.com>
To: "Email trigger recipients" <noreply@example.com>
Subject: EMAIL TRIGGER """+TempState.STATENAME[condition]+"""

Temperature alarm triggered at """+str(now)+""".

The current temperature state is """+TempState.STATENAME[condition]+""".

Sensor reading indicates a temperature of approximately """+str(newTemp)+""" degrees F. Readings are accurate to 0.8 degrees F.
"""
            )
