#!/usr/bin/env python
import RPi.GPIO as GPIO
import MFRC522
import signal

continue_reading = True

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
        print("Found Card")
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    if status == MIFAREReader.MI_OK:
        print("UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)
        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
        print("\n")
        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            data = []
            for i in range (0,16):
                data.append(0x01 + i)
            print("Before: ")
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_Write(8, data)
            print("After: ")
            MIFAREReader.MFRC522_Read(8)
            # Stop
            MIFAREReader.MFRC522_StopCrypto1()

            # Make sure to stop reading for cards
            continue_reading = False
        else:
            print("Authentication error")
