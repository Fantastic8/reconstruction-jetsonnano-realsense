import pyrealsense2 as rs
import numpy as np
import scipy.misc
import cv2

'''
CONFIG
'''
IMG_WIDTH = 1280
IMG_HEIGHT = 720

# render images
def renderImage(title, image):
    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Align Example', image)

# print profile of realsense frames
def printProfile(frames):
    for f in frames:
        print(f.profile)

# align depth image
def standardize(npa:np, distance:int):
    npa[npa < 1500] = 2
    npa[npa >= 1500] = 0


# Create a context object. This object owns the handles to all connected realsense devices
pipeline = rs.pipeline()

# Config realsense
config = rs.config()
config.enable_stream(rs.stream.depth, IMG_WIDTH, IMG_HEIGHT)
config.enable_stream(rs.stream.color, IMG_WIDTH, IMG_HEIGHT)


# start streaming
profile = pipeline.start(config)

# getting the depth sensor's depth scale
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print('Depth Scale is: ', depth_scale)

# We will be removing the background of objects more than clipping_distance_in_meters metters away
clipping_distance_in_meters = 1
clipping_distance = clipping_distance_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames
align_to = rs.stream.color
align = rs.align(align_to)

# Streaming loop
try:
    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()

        # Align the depth fram to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Remove background - Set pixels further than clipping_distance to replace color
        replace_color = 0
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), replace_color, color_image)

        # Render image
        print('.')
        '''
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        images = np.hstack((bg_removed, depth_colormap))
        renderImage('Align Example', images)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
        '''
finally:
    pipeline.stop()

'''
# get frames
frames = pipeline.wait_for_frames()
printProfile(frames)

# get color and depth image
color = frames.get_color_frame()
depth = frames.get_depth_frame()

# get color and depth data
color_data = color.as_frame().get_data()
depth_data = depth.as_frame().get_data()

# convert data into numpy array
np_color_image = np.asanyarray(color_data)
np_depth_image = np.asanyarray(depth_data)

# make distance larger than {dist} black, else white
standardize(np_depth_image, 1500)

# save image
scipy.misc.toimage(np_color_image).save('color.png')
scipy.misc.toimage(np_depth_image, cmin=0, cmax=2).save('depth.png')
print('Done')
'''
'''
print(np_depth_image.shape)
for i in range(18):
    line = ''
    for j in range(32):
        line += str(np_depth_image[i*40][j*40])+' '
    print(line)

while True:
    # Create a pipeline object. This object configures the streaming camera and owns it's handle
    frames = pipeline.wait_for_frames()
    depth = frames.get_depth_frame()
    depth_data = depth.as_frame().get_data()
    np_image = np.asanyarray(depth_data)
    scipy.misc.toimage(np_image, cmin=0.0, cmax=1.0).save('outfile.png')
'''

'''
    if not depth:
        continue
    # Print a simple text-based representation of the image, by breaking it into 10x20 pixel regions and approximating the coverage of pixels within one meter
    coverage = [0]*64
    for y in range(480):
        for x in range(640):
            dist = depth.get_distance(x, y)
            print(dist)
            if 0 < dist and dist < 1:
                coverage[int(x/10)] += 1
        if y%20 is 19:
            line = ""
            for c in coverage:
                line += " .:nhBXWW"[int(c/25)]
            coverage = [0]*64
            #print(line)
'''

