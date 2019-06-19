import Jetson.GPIO as GPIO
import time
import os
import pyrealsense2 as rs

'''
Config
'''

PIN_BUTTON = 18
PIN_RED_LIGHT = 33
PIN_WHITE_LIGHT = 31

CAPTURE_FREQUENCY = 1

'''
GPIO set up
'''
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_RED_LIGHT, GPIO.OUT)
GPIO.setup(PIN_WHITE_LIGHT, GPIO.OUT)

# Initial Condition - Red Light ON indicates program running, while light ON indicates camera taking pictures
GPIO.output(PIN_RED_LIGHT, GPIO.HIGH)
GPIO.output(PIN_WHITE_LIGHT, GPIO.LOW)

'''
Function
'''
def capture():
    os.system('rs-save-to-disk')


def rename(sequence):
    os.system('mv rs-save-to-disk-output-Depth.png D_' + str(sequence) + '.png')
    os.system('mv rs-save-to-disk-output-Color.png C_' + str(sequence) + '.png')

'''
Main
'''
try:
    print('Running')
    sequence = 0
    while True:
        print('Taking Pictures ...')
        time.sleep(CAPTURE_FREQUENCY)
        GPIO.output(PIN_WHITE_LIGHT, GPIO.HIGH)
        capture()
        rename(sequence)
        sequence += 1
        GPIO.output(PIN_WHITE_LIGHT, GPIO.LOW)


except KeyboardInterrupt:
    print('Exiting')
    GPIO.output(PIN_RED_LIGHT, GPIO.LOW)
    GPIO.cleanup()