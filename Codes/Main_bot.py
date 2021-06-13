from skyfield.api import N, E, wgs84
from skyfield.api import load

from time import strftime
import string
import pynmea2
import serial
import time

import datetime
import telepot
import subprocess
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import CPUTemperature

import sys
import smbus
import math

from imusensor.MPU9250 import MPU9250


address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()



GPIO.setmode(GPIO.BCM)
# GPIO.setup(led1, GPIO.OUT) # Declaring the output pin
# GPIO.setup(led2, GPIO.OUT) # Declaring the output pin
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#Button to GPIO4


DIR1 = 20
STEP1 = 21
DIR2 = 12
STEP2 = 16
EN1 = 18
EN2 = 23
CW =1
CCW =0

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR1, GPIO.OUT)
GPIO.setup(STEP1, GPIO.OUT)
GPIO.output(DIR1,CW)
GPIO.setup(DIR2, GPIO.OUT)
GPIO.setup(STEP2, GPIO.OUT)
GPIO.output(DIR2,CW)
GPIO.setup(EN1, GPIO.OUT)
GPIO.setup(EN2, GPIO.OUT)




def handle(msg):
    chat_id = msg['chat']['id'] # Receiving the message from telegram
    command = msg['text']   # Getting text from the message
    print ('Incoming...')
    print(command)
    
    content_type, chat_type, chat_id = telepot.glance(msg)
    keyboard = ReplyKeyboardMarkup(keyboard=[['Moon', 'Sun'], ['Mars', 'Venus']])
    # if content_type == 'text':
    #         if msg['text'] == '/key':
    #             bot.sendMessage(chat_id, 'testing custom keyboard',
    #                             reply_markup=ReplyKeyboardMarkup(
    #                                 keyboard=[
    #                                     [KeyboardButton(text="Yes"), KeyboardButton(text="No")]
    #                                 ]
    #                             ))
    # Comparing the incoming message to send a reply according to it
    # if command == 'Menu':
    #     bot.sendMessage (chat_id, str("Which sky object you want to observe?\n/Moon\n/Mars\n/Sun\n/Venus"))
    #     chat_id = msg['chat']['id'] # Receiving the message from telegram
    #     command = msg['text']   # Getting text from the message


    if command =='Moon':
        
        i = 0
        while i<1:
            # done1, done2 = 0
            port = "/dev/ttyS0"    # Raspberry Pi 3
            #port="/dev/ttyAMA0"
            ser=serial.Serial(port, baudrate=9600, timeout=0.5)
            dataout = pynmea2.NMEAStreamReader()
            newdata=ser.readline()

            if newdata[0:6] == "$GPRMC":
                newmsg=pynmea2.parse(newdata)
                lat=newmsg.latitude
                lng=newmsg.longitude
                ti = newmsg.timestamp
                da = newmsg.datestamp
                gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
                
                    
                planets = load('de421.bsp')
                earth, pla = planets['earth'], planets['moon']
                ts = load.timescale()
                u = datetime.datetime.utcnow()
                #t = ts.now()
                yeear = int(u.strftime("%Y"))
                moonth = int(u.strftime("%m"))
                daay = int(u.strftime("%d"))
                tii = str(ti).split(':')
                hoo = int(tii[0])
                mii = int(tii[1])
                see = float(tii[2])
                t = ts.utc(yeear, moonth, daay, hoo, mii, see)
                # print(t)


                my_location = earth + wgs84.latlon(float(lat) * N, float(lng) * E)
                astrometric = my_location.at(t).observe(pla)
                alt, az, d = astrometric.apparent().altaz()


                # print(str(alt))
                # print(str(az))

                #COMPUTING ALTITUDE ROTATING DEGREE
                alt_deg = str(alt).index('deg')
                alt_min = str(alt).index('\'')
                alt_sec = str(alt).index('\"')
                alt_DD = float(str(alt)[:alt_deg])+(float(str(alt)[alt_deg+4:alt_min])/60.0) + (float(str(alt)[alt_min+2:alt_sec])/3600)
                print(alt_DD)

                bot.sendMessage (chat_id, str(alt_DD))

                        
                #COMPUTING AZIMUTH ROTATING DEGREE
                az_deg = str(az).index('deg')
                az_min = str(az).index('\'')
                az_sec = str(az).index('\"')
                az_DD = float(str(az)[:az_deg])+(float(str(az)[az_deg+4:az_min])/60.0) + (float(str(az)[az_min+2:az_sec])/3600)
                print(az_DD)

                bot.sendMessage (chat_id, str(az_DD))

                i = i+1
        if (alt_DD > 0 and alt_DD < 60):
        
            GPIO.output(EN2,GPIO.HIGH)
            GPIO.output(DIR1,CCW)

            steps1 = int((az_DD*10000)/7.297)
            print(steps1)
            for x in range(steps1):
                GPIO.output(STEP1,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP1,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN2,GPIO.LOW)

            GPIO.output(EN1,GPIO.HIGH)
            GPIO.output(DIR2,CW)
            
            steps2 = int((alt_DD*10000)/7.167)
            print(steps2)
            for x in range(steps2):
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN1,GPIO.LOW)

            subprocess.call('fswebcam -r 1280x720 --no-banner usb_image.jpg', shell=True)
            bot.sendPhoto(chat_id, photo=open('usb_image.jpg', 'rb'))

        else:
            bot.sendMessage (chat_id, str("Out of visible zone"))

    elif command =='Mars':
        
        i = 0
        while i<1:
            # done1, done2 = 0
            port = "/dev/ttyS0"    # Raspberry Pi 3
            #port="/dev/ttyAMA0"
            ser=serial.Serial(port, baudrate=9600, timeout=0.5)
            dataout = pynmea2.NMEAStreamReader()
            newdata=ser.readline()

            if newdata[0:6] == "$GPRMC":
                newmsg=pynmea2.parse(newdata)
                lat=newmsg.latitude
                lng=newmsg.longitude
                ti = newmsg.timestamp
                da = newmsg.datestamp
                gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
                
                    
                planets = load('de421.bsp')
                earth, pla = planets['earth'], planets['mars']
                ts = load.timescale()
                u = datetime.datetime.utcnow()
                #t = ts.now()
                yeear = int(u.strftime("%Y"))
                moonth = int(u.strftime("%m"))
                daay = int(u.strftime("%d"))
                tii = str(ti).split(':')
                hoo = int(tii[0])
                mii = int(tii[1])
                see = float(tii[2])
                t = ts.utc(yeear, moonth, daay, hoo, mii, see)
                # print(t)


                my_location = earth + wgs84.latlon(float(lat) * N, float(lng) * E)
                astrometric = my_location.at(t).observe(pla)
                alt, az, d = astrometric.apparent().altaz()


                # print(str(alt))
                # print(str(az))

                #COMPUTING ALTITUDE ROTATING DEGREE
                alt_deg = str(alt).index('deg')
                alt_min = str(alt).index('\'')
                alt_sec = str(alt).index('\"')
                alt_DD = float(str(alt)[:alt_deg])+(float(str(alt)[alt_deg+4:alt_min])/60.0) + (float(str(alt)[alt_min+2:alt_sec])/3600)
                print(alt_DD)

                bot.sendMessage (chat_id, str(alt_DD))

                        
                #COMPUTING AZIMUTH ROTATING DEGREE
                az_deg = str(az).index('deg')
                az_min = str(az).index('\'')
                az_sec = str(az).index('\"')
                az_DD = float(str(az)[:az_deg])+(float(str(az)[az_deg+4:az_min])/60.0) + (float(str(az)[az_min+2:az_sec])/3600)
                print(az_DD)

                bot.sendMessage (chat_id, str(az_DD))

                i = i+1
        if (alt_DD > 0 and alt_DD < 60):
        
            GPIO.output(EN2,GPIO.HIGH)
            GPIO.output(DIR1,CCW)

            steps1 = int((az_DD*10000)/7.297)
            print(steps1)
            for x in range(steps1):
                GPIO.output(STEP1,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP1,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN2,GPIO.LOW)

            GPIO.output(EN1,GPIO.HIGH)
            GPIO.output(DIR2,CW)
            
            steps2 = int((alt_DD*10000)/7.167)
            print(steps2)
            for x in range(steps2):
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN1,GPIO.LOW)

            subprocess.call('fswebcam -r 1280x720 --no-banner usb_image.jpg', shell=True)
            bot.sendPhoto(chat_id, photo=open('usb_image.jpg', 'rb'))

        else:
            bot.sendMessage (chat_id, str("Out of visible zone"))

    elif command =='Sun':
        
        i = 0
        while i<1:
            # done1, done2 = 0
            port = "/dev/ttyS0"    # Raspberry Pi 3
            #port="/dev/ttyAMA0"
            ser=serial.Serial(port, baudrate=9600, timeout=0.5)
            dataout = pynmea2.NMEAStreamReader()
            newdata=ser.readline()

            if newdata[0:6] == "$GPRMC":
                newmsg=pynmea2.parse(newdata)
                lat=newmsg.latitude
                lng=newmsg.longitude
                ti = newmsg.timestamp
                da = newmsg.datestamp
                gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
                
                    
                planets = load('de421.bsp')
                earth, pla = planets['earth'], planets['Sun']
                ts = load.timescale()
                u = datetime.datetime.utcnow()
                #t = ts.now()
                yeear = int(u.strftime("%Y"))
                moonth = int(u.strftime("%m"))
                daay = int(u.strftime("%d"))
                tii = str(ti).split(':')
                hoo = int(tii[0])
                mii = int(tii[1])
                see = float(tii[2])
                t = ts.utc(yeear, moonth, daay, hoo, mii, see)
                # print(t)


                my_location = earth + wgs84.latlon(float(lat) * N, float(lng) * E)
                astrometric = my_location.at(t).observe(pla)
                alt, az, d = astrometric.apparent().altaz()


                # print(str(alt))
                # print(str(az))

                #COMPUTING ALTITUDE ROTATING DEGREE
                alt_deg = str(alt).index('deg')
                alt_min = str(alt).index('\'')
                alt_sec = str(alt).index('\"')
                alt_DD = float(str(alt)[:alt_deg])+(float(str(alt)[alt_deg+4:alt_min])/60.0) + (float(str(alt)[alt_min+2:alt_sec])/3600)
                print(alt_DD)

                bot.sendMessage (chat_id, str(alt_DD))

                        
                #COMPUTING AZIMUTH ROTATING DEGREE
                az_deg = str(az).index('deg')
                az_min = str(az).index('\'')
                az_sec = str(az).index('\"')
                az_DD = float(str(az)[:az_deg])+(float(str(az)[az_deg+4:az_min])/60.0) + (float(str(az)[az_min+2:az_sec])/3600)
                print(az_DD)

                bot.sendMessage (chat_id, str(az_DD))

                i = i+1
        if (alt_DD > 0 and alt_DD < 60):
        
            GPIO.output(EN2,GPIO.HIGH)
            GPIO.output(DIR1,CCW)

            steps1 = int((az_DD*10000)/7.297)
            print(steps1)
            for x in range(steps1):
                GPIO.output(STEP1,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP1,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN2,GPIO.LOW)

            GPIO.output(EN1,GPIO.HIGH)
            GPIO.output(DIR2,CW)
            
            steps2 = int((alt_DD*10000)/7.167)
            print(steps2)
            for x in range(steps2):
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN1,GPIO.LOW)

            subprocess.call('fswebcam -r 1280x720 --no-banner usb_image.jpg', shell=True)
            bot.sendPhoto(chat_id, photo=open('usb_image.jpg', 'rb'))

        else:
            bot.sendMessage (chat_id, str("Out of visible zone"))


    elif command =='Venus':
        
        i = 0
        while i<1:
            # done1, done2 = 0
            port = "/dev/ttyS0"    # Raspberry Pi 3
            #port="/dev/ttyAMA0"
            ser=serial.Serial(port, baudrate=9600, timeout=0.5)
            dataout = pynmea2.NMEAStreamReader()
            newdata=ser.readline()

            if newdata[0:6] == "$GPRMC":
                newmsg=pynmea2.parse(newdata)
                lat=newmsg.latitude
                lng=newmsg.longitude
                ti = newmsg.timestamp
                da = newmsg.datestamp
                gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
                
                    
                planets = load('de421.bsp')
                earth, pla = planets['earth'], planets['venus']
                ts = load.timescale()
                u = datetime.datetime.utcnow()
                #t = ts.now()
                yeear = int(u.strftime("%Y"))
                moonth = int(u.strftime("%m"))
                daay = int(u.strftime("%d"))
                tii = str(ti).split(':')
                hoo = int(tii[0])
                mii = int(tii[1])
                see = float(tii[2])
                t = ts.utc(yeear, moonth, daay, hoo, mii, see)
                # print(t)


                my_location = earth + wgs84.latlon(float(lat) * N, float(lng) * E)
                astrometric = my_location.at(t).observe(pla)
                alt, az, d = astrometric.apparent().altaz()


                # print(str(alt))
                # print(str(az))

                #COMPUTING ALTITUDE ROTATING DEGREE
                alt_deg = str(alt).index('deg')
                alt_min = str(alt).index('\'')
                alt_sec = str(alt).index('\"')
                alt_DD = float(str(alt)[:alt_deg])+(float(str(alt)[alt_deg+4:alt_min])/60.0) + (float(str(alt)[alt_min+2:alt_sec])/3600)
                print(alt_DD)

                bot.sendMessage (chat_id, str(alt_DD))

                        
                #COMPUTING AZIMUTH ROTATING DEGREE
                az_deg = str(az).index('deg')
                az_min = str(az).index('\'')
                az_sec = str(az).index('\"')
                az_DD = float(str(az)[:az_deg])+(float(str(az)[az_deg+4:az_min])/60.0) + (float(str(az)[az_min+2:az_sec])/3600)
                print(az_DD)

                bot.sendMessage (chat_id, str(az_DD))

                i = i+1
        if (alt_DD > 0 and alt_DD < 60):
        
            GPIO.output(EN2,GPIO.HIGH)
            GPIO.output(DIR1,CCW)

            steps1 = int((az_DD*10000)/7.297)
            print(steps1)
            for x in range(steps1):
                GPIO.output(STEP1,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP1,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN2,GPIO.LOW)

            GPIO.output(EN1,GPIO.HIGH)
            GPIO.output(DIR2,CW)
            
            steps2 = int((alt_DD*10000)/7.167)
            print(steps2)
            for x in range(steps2):
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(0.00001)
            GPIO.output(EN1,GPIO.LOW)

            subprocess.call('fswebcam -r 1280x720 --no-banner usb_image.jpg', shell=True)
            bot.sendPhoto(chat_id, photo=open('usb_image.jpg', 'rb'))

        else:
            bot.sendMessage (chat_id, str("Out of visible zone"))

    elif command =='/capture':
        subprocess.call('fswebcam -r 1280x720 --no-banner usb_image.jpg', shell=True)
        bot.sendPhoto(chat_id, photo=open('usb_image.jpg', 'rb'))

    elif command == '/Altitude_Up':
        
        bot.sendMessage (chat_id, str("Going up!"))
        GPIO.output(DIR2,CCW)
        GPIO.output(EN1,GPIO.HIGH)
        for x in range (10000):
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(0.00001)
        GPIO.output(EN1,GPIO.LOW)

    
    elif command == '/Altitude_Down':
        
        bot.sendMessage (chat_id, str("Going down!"))
        GPIO.output(DIR2,CW)
        GPIO.output(EN1,GPIO.HIGH)
        for x in range (10000):
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(0.00001)
        GPIO.output(EN1,GPIO.LOW)


    elif command == '/Azimuth_Clk':
        
        bot.sendMessage (chat_id, str("Clockwise!"))
        GPIO.output(DIR1,CW)
        GPIO.output(EN2,GPIO.HIGH)
        for x in range(10000):
            GPIO.output(STEP1,GPIO.HIGH)
            sleep(0.00001)
            GPIO.output(STEP1,GPIO.LOW)
            sleep(0.00001)
        GPIO.output(EN2,GPIO.LOW)

    elif command == '/Azimuth_AntiClk':
        
        bot.sendMessage (chat_id, str("Anticlockwise!"))
        GPIO.output(DIR1,CCW)
        GPIO.output(EN2,GPIO.HIGH)
        for x in range(10000):
            GPIO.output(STEP1,GPIO.HIGH)
            sleep(0.00001)
            GPIO.output(STEP1,GPIO.LOW)
            sleep(0.00001)
        GPIO.output(EN2,GPIO.LOW)


    elif command == '/Home':
        bot.sendMessage (chat_id, str("Home!"))
        
        GPIO.output(DIR2,CCW)
        GPIO.output(EN1,GPIO.HIGH)

        for x in range(83717): 
            if (GPIO.input(4)== 0):
                GPIO.output(STEP2,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP2,GPIO.LOW)
                sleep(0.00001)

            elif (GPIO.input(4)== 1): 
                GPIO.output(EN1,GPIO.LOW) 
                x = 90000
                print("I AM HOME _ALTITUDE")
        sleep(0.5)



        GPIO.output(DIR1,CCW)
        GPIO.output(EN2,GPIO.HIGH)

        for x in range(493353): 
            
            imu.readSensor()
            imu.computeOrientation()
            xGaussData = float(imu.MagVals[0])*0.48828125
            yGaussData = float(imu.MagVals[1])*0.48828125
            if (xGaussData==0):
                    if (yGaussData < 0):
                            D = 90
                    elif (yGaussData >=0 ):
                            D = 0
            elif (xGaussData!=0):
                    D = math.atan(yGaussData/xGaussData)*(180/math.pi)
                    if (D > 360):
                            D = D-360
                    elif (D < 0):
                            D = D + 360
            if (D <= 360 and D >= 350):
                GPIO.output(EN2,GPIO.LOW) 
                x = 500000
                print("I AM HOME _AZIMUTH")

            else: 
                GPIO.output(STEP1,GPIO.HIGH)
                sleep(0.00001)
                GPIO.output(STEP1,GPIO.LOW)
                sleep(0.00001)
                
        sleep(0.5)





# Enter your telegram token below
bot = telepot.Bot('1367164646:AAEcGkilV7SRAL0AZfHwX_7sjp8xPilU_Zs')
print (bot.getMe())

# Start listening to the telegram bot and whenever a message is  received, the handle function will be called.
MessageLoop(bot, handle).run_as_thread()
print ('GPIOTEL 2.00 at your service...')

while 1:
    sleep(10)

