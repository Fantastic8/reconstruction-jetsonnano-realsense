import pyrealsense2 as rs
import numpy as np
import scipy.misc
import time
from threading import Thread
import queue
import traceback
import Jetson.GPIO as GPIO
import gc

'''''''''''''''''''''''''''
        CONFIGURATION
'''''''''''''''''''''''''''
IMG_WIDTH = 1280
IMG_HEIGHT = 720

OUTPUTDIR = 'output/'
CAPTURE_CYCLE = 0.2
CLIPPING_DISTANCE = 2

QUEUE_SIZE = 100
SLIDING_WINDOW = 2

PIN_RED_LIGHT = 33
PIN_WHITE_LIGHT = 31

'''''''''''''''''''''''''''
    GLOBAL PARAMETER
'''''''''''''''''''''''''''
isRunning = True
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
        scipy.misc.toimage(npImage, cmin=CLIPPED_LOW, cmax=CLIPPED_HIGH).save(OUTPUTDIR+prefix+str(sequence)+'_mask.png')
    else:
        scipy.misc.toimage(npImage).save(OUTPUTDIR+prefix + str(sequence) + '.png')
    print('--> SAVE '+prefix+str(sequence)+'.png')


# print profile of frame
def printProfile(frames):
    for f in frames:
        print(f.profile)


# Capture Thread - capture depth images and depth images
def capture_filter_thread(color_np_queue, mask_np_queue):
    global depth_scale, isRunning
    print('> Capture Thread Started')
    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()

    try:
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

        '''''''''''''''''''''''''''
            Create Filters
        '''''''''''''''''''''''''''
        # Decimation Filter - change resolution size!
        # decimation = rs.decimation_filter()
        # decimation.set_option(rs.option.filter_magnitude, 0.5)

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

        frameset = None
        filtered_depth_frame = None

        # Skip 5 first frames to give the Auto-Exposure time to adjust
        for x in range(5):
            pipeline.wait_for_frames()

        while isRunning:
            print('---> Capture One Frame')
            frameset = pipeline.wait_for_frames()

            # Validate that both frames are valid
            if not frameset:
                continue

            # put aligned frameset into queue, queue will be blocked if queue is full. Timeout = 5 to throw exception
            alignment = align.process(frameset)

            for x in range(SLIDING_WINDOW):
                # get frame
                frameset = alignment
                filtered_depth_frame = frameset.get_depth_frame()
                # Filtering
                filtered_depth_frame = depth_to_disparity.process(filtered_depth_frame)
                filtered_depth_frame = spatial.process(filtered_depth_frame)
                filtered_depth_frame = temporal.process(filtered_depth_frame)
                filtered_depth_frame = disparity_to_depth.process(filtered_depth_frame)
                filtered_depth_frame = hole_filling.process(filtered_depth_frame)

            color_np_queue.put(np.asanyarray(frameset.get_color_frame().get_data()))
            mask_np_queue.put(np.asanyarray(filtered_depth_frame.get_data()))
            del frameset
            gc.collect()

            time.sleep(CAPTURE_CYCLE)
    except:
        traceback.print_exc()
        rs.log_to_console(rs.log_severity.debug)
    finally:
        pipeline.stop()
        print('> Capture Thread Stopped')


# Filter Thread - filter images
def save_thread(color_np_queue, mask_np_queue):
    global frameset_queue, isRunning

    print('> Filter & Save Thread Started')
    try:
        # visualising the data
        #colorizer = rs.colorizer()

        sequence = 0

        '''''''''''''''''''''''''''
            Create Filters
        '''''''''''''''''''''''''''
        # Decimation Filter - change resolution size!
        # decimation = rs.decimation_filter()
        # decimation.set_option(rs.option.filter_magnitude, 0.5)

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

        frameset = None
        filtered_depth_frame = None
        while isRunning:
            time.sleep(0.2)
            while not frameset_queue.empty():
                time.sleep(0.2)
                print('---> Wait for Frames')
                # filter frames
                for x in range(SLIDING_WINDOW):
                    # print('----> Get Sliding Window')
                    if frameset_queue.empty():
                        break
                    # get depth frame
                    frameset = frameset_queue.get(False)
                    filtered_depth_frame = frameset.get_depth_frame()
                    # Filtering
                    # filtered_depth_frame = decimation.process(filtered_depth_frame)
                    filtered_depth_frame = depth_to_disparity.process(filtered_depth_frame)
                    filtered_depth_frame = spatial.process(filtered_depth_frame)
                    filtered_depth_frame = temporal.process(filtered_depth_frame)
                    filtered_depth_frame = disparity_to_depth.process(filtered_depth_frame)
                    filtered_depth_frame = hole_filling.process(filtered_depth_frame)
                print('---> Got One')

                # Save Images
                color_np = np.asanyarray(frameset.get_color_frame().get_data())
                saveImage(color_np, 'IMAGE_', sequence)

                # save depth image
                #saveImage(np.asanyarray(frameset.get_depth_frame().get_data()), 'DEPTH_', sequence)

                filtered_depth_np = np.asanyarray(filtered_depth_frame.get_data())
                # save filtered depth frame
                #saveImage(filtered_depth_np, 'FILTERED_DEPTH_', sequence)

                # save colorized filtered depth frame
                #saveImage(np.asanyarray(colorizer.colorize(filtered_depth_frame).get_data()), 'COLORIZED_FILTERED_DEPTH_', sequence)

                # save mask from clipped filtered depth frame
                saveImage(createMask(filtered_depth_np, CLIPPING_DISTANCE), 'IMAGE_', sequence, True)

                # save clipped filtered color frame
                #replace_color = 0
                #filtered_depth_image_3d = np.dstack((filtered_depth_np, filtered_depth_np, filtered_depth_np))
                #clipped_filtered_color_np = np.where((filtered_depth_image_3d > (CLIPPING_DISTANCE / depth_scale)) | (filtered_depth_image_3d <= 0), replace_color, color_np)
                #saveImage(clipped_filtered_color_np, 'CLIPPED_FILTERED_COLOR_', sequence)

                sequence += 1
    except:
        traceback.print_exc()
    finally:
        print('> Filter & Save Thread Stopped')

'''''''''''''''''''''''''''
            Main
'''''''''''''''''''''''''''
if __name__ == '__main__':

    # queue<frame>, capture thread -> filterSave thread
    #frameset_queue = queue.Queue(SLIDING_WINDOW * QUEUE_SIZE)

    color_np_queue = queue.Queue(SLIDING_WINDOW * QUEUE_SIZE)
    mask_np_queue = queue.Queue(SLIDING_WINDOW * QUEUE_SIZE)


    #captureThread = Thread(target=capture_thread, args=(frameset_queue,))
    captureFilterThread = Thread(target=capture_filter_thread, args=(color_np_queue, mask_np_queue,))
    captureFilterThread.start()

    #saveThread = Thread(target=save_thread)
    #saveThread.start()

    while(input()!='q'):
        time.sleep(0.1)
    isRunning = False
    GPIO.output(PIN_RED_LIGHT, GPIO.LOW)
    GPIO.cleanup()

