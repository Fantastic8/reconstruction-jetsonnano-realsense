'''
@author Mark Zhang
@create May 30, 2019
'''

import pyrealsense2 as rs
import numpy as np
import scipy.misc
import cv2
import time
import Jetson.GPIO as GPIO
import os

'''''''''''''''''''''''''''
        CONFIGURATION
'''''''''''''''''''''''''''
# Camera Configuration
IMG_WIDTH = 1280
IMG_HEIGHT = 720
CAPTURE_CYCLE = 0


# Image file Configuration
dir = time.strftime('%H_%M_%S', time.localtime(time.time()))
OUTPUTDIR = 'output/'+dir+'/'
os.mkdir(OUTPUTDIR)
ZEROFILL = 3
CLIPPING_DISTANCE = 3

# Program Configuration
SLIDING_WINDOW = 1

# GPIO Configuration
PIN_RED_LIGHT = 33
PIN_WHITE_LIGHT = 31

'''''''''''''''''''''''''''
    GLOBAL PARAMETER
'''''''''''''''''''''''''''
CLIPPED_LOW = 0
CLIPPED_HIGH = 2

depth_scale = 0.001

'''''''''''''''''''''''''''
    GPIO SET UP
'''''''''''''''''''''''''''
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_RED_LIGHT, GPIO.OUT)
GPIO.setup(PIN_WHITE_LIGHT, GPIO.OUT)

# Initial Condition - Red Light ON indicates program running, while light ON indicates camera taking pictures
GPIO.output(PIN_RED_LIGHT, GPIO.HIGH)
GPIO.output(PIN_WHITE_LIGHT, GPIO.LOW)

'''''''''''''''''''''''''''
        Functions
'''''''''''''''''''''''''''
# clipping depth image
def createMask(depth_np:np, distance:float):
    global CLIPPED_LOW, CLIPPED_HIGH, depth_scale

    # We will be removing the background of objects more than clipping_distance_in_meters metters away
    clipping_distance = distance / depth_scale
    depth_np[depth_np < clipping_distance] = CLIPPED_HIGH
    depth_np[depth_np >= clipping_distance] = CLIPPED_LOW
    return depth_np


# save image
def saveImage(npImage:np, prefix:str, sequence:int, mask:bool=False):
    global CLIPPED_LOW, CLIPPED_HIGH
    if mask:
        scipy.misc.toimage(npImage, cmin=CLIPPED_LOW, cmax=CLIPPED_HIGH).save(OUTPUTDIR+prefix+str(sequence).zfill(ZEROFILL)+'_mask.png')
    else:
        scipy.misc.toimage(npImage).save(OUTPUTDIR+prefix + str(sequence).zfill(ZEROFILL) + '.png')
    print('--> SAVE '+prefix+str(sequence)+'.png')


def renderImage(title, image):
    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(title, image)

def printProfile(frames):
    for f in frames:
        print(f.profile)


def standardize(npa:np, distance:int):
    npa[npa < distance] = 2
    npa[npa >= distance] = 0

'''''''''''''''''''''''''''
        Main
'''''''''''''''''''''''''''

# Create a context object. This object owns the handles to all connected realsense devices
pipeline = rs.pipeline()

# Config realsense
config = rs.config()
config.enable_stream(rs.stream.depth, IMG_WIDTH, IMG_HEIGHT)
config.enable_stream(rs.stream.color, IMG_WIDTH, IMG_HEIGHT)

# Start streaming
profile = pipeline.start(config)

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames
align_to = rs.stream.color
align = rs.align(align_to)

# Get the depth sensor's depth scale
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
# print('Depth Scale is: ', depth_scale)

# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):
    pipeline.wait_for_frames()

# visualising the data
#colorizer = rs.colorizer()

'''''''''''''''''''''''''''
    Create Filters
'''''''''''''''''''''''''''
# Decimation Filter - change resolution size!
#decimation = rs.decimation_filter()
#decimation.set_option(rs.option.filter_magnitude, 0.5)

# Spatial Filter
spatial = rs.spatial_filter()
spatial.set_option(rs.option.filter_magnitude, 5)
spatial.set_option(rs.option.filter_smooth_alpha, 1)
spatial.set_option(rs.option.filter_smooth_delta, 50)
spatial.set_option(rs.option.holes_fill, 3)

# Temporal Filter
temporal = rs.temporal_filter()

# Hole Filling Filter
hole_filling = rs.hole_filling_filter()

# Disparity Transform
depth_to_disparity = rs.disparity_transform(True)
disparity_to_depth = rs.disparity_transform(False)

'''''''''''''''''''''''''''
        Streaming
'''''''''''''''''''''''''''
try:
    print('> Pipeline Started')
    frameset = None
    filtered_frame = None
    sequence = 0
    while True:
        for x in range(SLIDING_WINDOW):
            frameset = pipeline.wait_for_frames()
            # Validate that both frames are valid
            if not frameset:
                x -= 1
                continue
            # Align the depth frame to color frame
            frameset = align.process(frameset)

            # get depth frame
            filtered_frame = frameset.get_depth_frame()
            # Filtering
            #filtered_frame = decimation.process(filtered_frame)
            filtered_frame = depth_to_disparity.process(filtered_frame)
            filtered_frame = spatial.process(filtered_frame)
            filtered_frame = temporal.process(filtered_frame)
            filtered_frame = disparity_to_depth.process(filtered_frame)
            filtered_frame = hole_filling.process(filtered_frame)

        # white light on
        GPIO.output(PIN_WHITE_LIGHT, GPIO.HIGH)
        # Raw Depth image
        #depth_np = np.asanyarray(frameset.get_depth_frame().get_data())
        #saveImage(depth_np, 'Depth_', sequence)

        print('----------')
        # Raw Color image
        color_np = np.asanyarray(frameset.get_color_frame().get_data())
        saveImage(color_np, 'IMAGE_', sequence)

        # Filtered depth image
        #filtered_np = np.asanyarray(filtered_frame.get_data())
        #saveImage(filtered_np, 'Filtered_Depth_', sequence)

        # Colorized Filtered depth image
        #colorized_filtered_np = np.asanyarray(colorizer.colorize(filtered_frame).get_data())
        #saveImage(colorized_filtered_np, 'Colorized_Filtered_Depth_', sequence)

        filtered_depth_np = np.asanyarray(filtered_frame.get_data())
        # Clipped Filtered depth image
        clipped_filtered_np = createMask(filtered_depth_np, CLIPPING_DISTANCE)
        saveImage(clipped_filtered_np, 'IMAGE_', sequence, True)

        #replace_color = 0
        #filtered_depth_image_3d = np.dstack((filtered_depth_np, filtered_depth_np, filtered_depth_np))
        #clipped_filtered_color_np = np.where((filtered_depth_image_3d > (CLIPPING_DISTANCE / depth_scale)) | (filtered_depth_image_3d <= 0), replace_color, color_np)
        #saveImage(clipped_filtered_color_np, 'VIEW_', sequence)

        # white light on
        GPIO.output(PIN_WHITE_LIGHT, GPIO.LOW)
        sequence += 1
        time.sleep(CAPTURE_CYCLE)
finally:
    pipeline.stop()
    GPIO.output(PIN_RED_LIGHT, GPIO.LOW)
    GPIO.output(PIN_WHITE_LIGHT, GPIO.LOW)
    GPIO.cleanup()
    print('> Pipeline Stopped')

