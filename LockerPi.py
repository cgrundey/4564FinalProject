#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import MFRC522
import signal
import pika

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(false)

red = 4
green = 18
blue = 23

GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

Freq = 100
RED = GPIO.PWM(red, Freq)
GREEN = GPIO.PWM(green, Freq)
BLUE = GPIO.PWM(blue, Freq)

RED.start(100)
GREEN.start(100)
BLUE.start(100)

"get this from RFID sensor"
lockerID = ''
auth_key = ''
rabbitExchange = 'BlacksburgLockers'

credentials = pika.PlainCredentials('Apple', 'Pie')
parameters = pika.ConnectionParameters(sys.argv[1], virtual_host='team_13_host', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

authorized = False

continue_reading = True

def master_callback(ch, method, properties, body):
    channel.stop_consuming()
	print("Response: " + str(body))
    if body == "valid":
        authorized = True
    else:
        authorized = False

def end_read(signal,frame):
    global continue_reading
    print("Ending...")
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
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        MIFAREReader.MFRC522_SelectTag(uid)
        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            # send credentials via RabbitMQ here
            # publish to lockerID queue
            channel.basic_publish(exchange=rabbitExchange, routing_key=lockerID, body=uid + "," + lockerID)
            # consume once
            channel.basic_consume(exchange=rabbitExchange, queue=lockerID, no_ack=True)

            # output status to led
            if authorized:
                # success
                RED.ChangeDutyCycle(0)
                GREEN.ChangeDutyCycle(100)
                BLUE.ChangeDutyCycle(0)
            else:
                # failure
                RED.ChangeDutyCycle(100)
                GREEN.ChangeDutyCycle(0)
                BLUE.ChangeDutyCycle(0)
            sleep(2.5)
            RED.ChangeDutyCycle(0)
            GREEN.ChangeDutyCycle(0)
            BLUE.ChangeDutyCycle(0)
            authorized = False
        else:
            print("Authentication error")
            RED.ChangeDutyCycle(100)
            GREEN.ChangeDutyCycle(0)
            BLUE.ChangeDutyCycle(0)
            sleep(2.5)
            RED.ChangeDutyCycle(0)
            GREEN.ChangeDutyCycle(0)
            BLUE.Chan
