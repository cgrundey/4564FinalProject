#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import MFRC522
import signal

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

red = 11
green = 13
blue = 15

GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

Freq = 100
RED = GPIO.PWM(red, Freq)
GREEN = GPIO.PWM(green, Freq)
BLUE = GPIO.PWM(blue, Freq)

blueval = 100
RED.start(100)
GREEN.start(20)
BLUE.start(60)

def refreshlight():
    global blueval
    blueval += 1

def lightPulse(r,g,b):
    RED.ChangeDutyCycle(r)
    GREEN.ChangeDutyCycle(g)
    BLUE.ChangeDutyCycle(b)
    sleep(2.5)
    RED.ChangeDutyCycle(100)
    GREEN.ChangeDutyCycle(30)
    BLUE.ChangeDutyCycle(0)

authorized = True

continue_reading = True

def end_read(signal,frame):
    global continue_reading
    print("/nEnding...")
    continue_reading = False
    GPIO.cleanup()
signal.signal(signal.SIGINT, end_read)

MIFAREReader = MFRC522.MFRC522()

while continue_reading:
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:
        print("Got it,")
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        uid = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
        print("Authorizing UID: " + uid + " ...")
        # output status to led
        if uid == '126227175133': # success
            lightPulse(0,100,0)
        else:                     # failure
            lightPulse(100,0,0)
    refreshlight()
