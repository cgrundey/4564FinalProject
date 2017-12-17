#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import MFRC522 # RFID library
import signal  # EOF signal
import pika    # RabbitMQ library
import sys

# EOF
def end_read(signal,frame):
    global continue_reading
    print("Ending...")
    continue_reading = False
    GPIO.cleanup()
signal.signal(signal.SIGINT, end_read)

# __________________________GPIO_SETUP__________________________________
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

RED.start(0)
GREEN.start(0)
BLUE.start(100)

def lightPulse(r,g,b):
    RED.ChangeDutyCycle(r)
    GREEN.ChangeDutyCycle(g)
    BLUE.ChangeDutyCycle(b)
    sleep(2.5)
    RED.ChangeDutyCycle(0)
    GREEN.ChangeDutyCycle(0)
    BLUE.ChangeDutyCycle(100)

# __________________________RABBITMQ_SETUP__________________________________
lockerID = ''
auth_key = ''
rabbitExchange = 'team_13'
try:
    credentials = pika.PlainCredentials('Apple', 'Pie')
    parameters = pika.ConnectionParameters(sys.argv[1], virtual_host='team_13_host', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=rabbitExchange, exchange_type="direct")
except:
    sys.exit('Unable to connect to RabbitMQ Server')

# LOOP VARIABLES
authorized = False
continue_reading = True
# RABBIT CALLBACK
def master_callback(ch, method, properties, body):
    channel.stop_consuming()
	print("Response: " + str(body))
    if body == "success":
        authorized = True
    else:
        authorized = False

MIFAREReader = MFRC522.MFRC522() # RFID sensor

# __________________________MAIN_LOOP__________________________________
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
            channel.basic_publish(exchange=rabbitExchange, routing_key=lockerID, body=uid)
            # consume once to get response
            channel.basic_consume(master_callback, queue=lockerID, no_ack=True)
            channel.start_consuming()
            # Rabbit Callback will modify authorized appropriately
            # output status to led
            if authorized: # success
                lightPulse(0,100,0) # GREEN
            else: # failure
                lightPulse(100,0,0) # RED
            authorized = False
        else:
            print("Authentication error")
            lightPulse(100,0,0) # RED
