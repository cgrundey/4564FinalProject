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
    continue_reading = False
    GPIO.cleanup()
    sys.exit("\nClosing...")
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

RED.start(14)
GREEN.start(0)
BLUE.start(40)

def lightPulse(r,g,b):
    RED.ChangeDutyCycle(r)
    GREEN.ChangeDutyCycle(g)
    BLUE.ChangeDutyCycle(b)
    sleep(2)
    RED.ChangeDutyCycle(14)
    GREEN.ChangeDutyCycle(0)
    BLUE.ChangeDutyCycle(40)

# __________________________RABBITMQ_SETUP__________________________________
lockerID = 'lock2'
rabbitExchange = 'team_13'
try:
    credentials = pika.PlainCredentials('Apple', 'Pie')
    parameters = pika.ConnectionParameters(sys.argv[1], virtual_host='team_13_host', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=rabbitExchange, exchange_type="direct")
    channel.queue_declare(queue=lockerID+"rcvVal")
    channel.queue_declare(queue=lockerID+"rcvAuth")
    print("Connected to RabbitMQ!\nLockerID: " + lockerID)
except:
    sys.exit('Unable to connect to RabbitMQ Server')

# LOOP VARIABLES
continue_reading = True
# RABBIT CALLBACK
def master_callback(ch, method, properties, body):
    if body == 'success':
        lightPulse(0,100,0)
        print("Authorized!")
    else:
        lightPulse(100,0,0)
        print("Not authorized.")
    channel.stop_consuming()

MIFAREReader = MFRC522.MFRC522() # RFID sensor

# __________________________MAIN_LOOP__________________________________
while continue_reading:
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:
        print("Reading card")
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        uid = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
        print("Authorizing UID: " + uid + " ...")
        # send credentials via RabbitMQ here
        # publish to lockerID queue
        channel.basic_publish(exchange=rabbitExchange, routing_key=lockerID+"rcvAuth", body=uid)
        #res = channel.queue_declare(queue=lockerID, durable=True, exclusive=False, auto_delete=False, passive=True)
        channel.basic_consume(master_callback, queue=lockerID+"rcvVal", no_ack=True)
        channel.start_consuming()
