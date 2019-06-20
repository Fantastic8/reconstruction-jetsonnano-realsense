# reconstruction-jetsonnano-realsense

## Introduction
This project is doing 3D reconstruction using Jetson nano and Intel realsense to capture images and reconstruct a mesh model on Google Cloud using openMVG and openMVS algorithm.


## Motivation

This project used openMVG and openMVS algorithm to construct a 3D mesh model of an object. To make algorithm faster and produce more accurate mesh model, RGB-Depth stereo camera was used to remove background of an image, and CUDA was used to speed up the process of processing images.


## Prerequisites

+ [Intel Realsense D435i](https://www.intelrealsense.com/depth-camera-d435i/)
+ [NVIDIA Jetson Nano](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-nano/)
+ A portable battery charger (Minimum 3A output)
+ A cloud server (Google Compute Engine was used for this project)


## Build

### Hardware

#### NVIDIA Jetson Nano

[Get started with Jetson Nano](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)

There is lots of helpful Jetson Nano resource on [JetsonHacksNano](https://github.com/JetsonHacksNano) Github.


#### Intel realsense D435i

After installed the system of Jetson nano and done with 

```
sudo apt update
```
and

```
sudo apt upgrade
``` 
[Intel® RealSense™ SDK 2.0](https://github.com/IntelRealSense/librealsense) needs to be installed on Jetson Nano board in order to make board receives images from camera properly.

I found a [video](https://www.youtube.com/watch?v=NonBlt-wKCI) on youtube that shows how to install RealSense SDK on Jetson Nano. Here's the [repository](https://github.com/JetsonHacksNano/installLibrealsense) in the video which can easily install librealsense SDK. (Note: build with CUDA for this project

```
./installLibrealsense.sh --build_with_cuda
```
)

Next, build python3 [wrapper](https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python) of librealsense.

Unfortunately, after building librealsense SDK on Jetson Nano, the camera is unrecognizable for Jetson Nano. That's because the librealsense SDK doesn't support the current kernel of Jetson Nano. Here's the [turotial](https://github.com/IntelRealSense/librealsense/issues/3759#issuecomment-485263506) for rebuilding kernel of Jetson Nano.

This time, the camera can finally work nicely on board.


### Server


These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live syste.


# Installing

A step by step series of examples that tell you have to get a development environment running.

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo.

# Running the tests

Explain how to run the automated tests for this system.



# Deployment

Add additional notes about how to deploy this on a live system.


# Built With

+ SSH - Back end Framework
+ BootStrap - Front end Framework

![Design Flow](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/DesignFlow.png)

# Author

[@Mark Zhang](https://github.com/Fantastic8)


# Acknowledgments

This project has been supported by UCI MECPS program and advised by professor [@Rainer Dömer](http://www.cecs.uci.edu/~doemer/).

[![UCI MECPS](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/MECPSLOGO-01-300x85.png)](https://mecps.uci.edu/)