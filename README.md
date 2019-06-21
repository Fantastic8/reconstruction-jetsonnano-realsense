# reconstruction-jetsonnano-realsense

## Introduction
This project is doing 3D reconstruction using Jetson nano and Intel realsense to capture images and reconstruct a mesh model on Google Cloud using openMVG and openMVS algorithm.


## Motivation

This project used openMVG and openMVS algorithm to construct a 3D mesh model of an object. To make algorithm faster and produce more accurate mesh model, RGB-Depth stereo camera was used to remove background of an image, and CUDA was used to speed up the process of processing images.


## Design Flow

Below is the design flow of this project. Or you can see the poster to better understand this project [here](https://github.com/Fantastic8/reconstruction-jetsonnano-realsense/blob/master/media/poster.jpg).

![Design Flow](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/DesignFlow.png)

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

At this time, the camera can finally work nicely on board.


### Server

#### openMVG

Follow the [instruction](https://github.com/openMVG/openMVG) to install openMVG on Server.

#### openMVS

Follow the [instruction](https://github.com/cdcseacave/openMVS) to install openMVS on Server.


## Usage

### Jetson Nano

Download repository on your Jetson Nano.

```
git clone https://github.com/Fantastic8/reconstruction-jetsonnano-realsense.git
```

Enter "nano_realsense" folder.

```
cd reconstruction-jetsonnano-realsense/nano_realsense
```

Run python script, this script will create an "output" folder, and another folder inside the "output" folder named with time you run the script to store images. After running the script, you will get RGB image and Mask image sequence.

```
python3 depth_filter.py
```

### Server

Transfer RGB and Mask images to server.

Download repository on server.

```
git clone https://github.com/Fantastic8/reconstruction-jetsonnano-realsense.git
```

Enter "script" folder.

```
cd reconstruction-jetsonnano-realsense/script
```

Run script,

```
sudo bash mvgmvs.sh 1536 
```

For "mvgmvs.sh" script, it takes 6 parameters. See [documentation](https://openmvg.readthedocs.io/en/latest/software/SfM/SfMInit_ImageListing/) for more information.

```
1. focal
	[-f|–focal] (value in pixels)
2. describerMethod
	[-m|–describerMethod]
		Used method to describe an image:
			SIFT: (default),
			AKAZE_FLOAT: AKAZE with floating point descriptors,
			AKAZE_MLDB: AKAZE with binary descriptors.
3. describerPreset
	[-p|–describerPreset]
		Used to control the Image_describer configuration:
			NORMAL,
			HIGH,
			ULTRA: !!Can be time consuming!!
4. ratio
	[-r|-ratio]
		(Nearest Neighbor distance ratio, default value is set to 0.8).
			Using 0.6 is more restrictive => provides less false positive.
5. geometric_model
	[-g|-geometric_model]
		type of model used for robust estimation from the photometric putative matches
			f: Fundamental matrix filtering
			e: Essential matrix filtering
			h: Homography matrix filtering

6. nearest_matching_method
	[-n|–nearest_matching_method]
			AUTO: auto choice from regions type,
		For Scalar based descriptor you can use:
			BRUTEFORCEL2: BruteForce L2 matching for Scalar based regions descriptor,
			ANNL2: Approximate Nearest Neighbor L2 matching for Scalar based regions descriptor,
			CASCADEHASHINGL2: L2 Cascade Hashing matching,
			FASTCASCADEHASHINGL2: (default).
				L2 Cascade Hashing with precomputed hashed regions, (faster than CASCADEHASHINGL2 but use more memory).
		For Binary based descriptor you must use:
			BRUTEFORCEHAMMING: BruteForce Hamming matching for binary based regions descriptor,
```

It's ok that you don't know which parameter you want to use. You can simply run script "mvgmvsMulti.sh" to "Brute Force" all parameter combinations.

All you have to do is to add parameters you want to test in the array, and it will automatically go over all the combinations.

```
# ------ Image Listing parameter ------
# [-f|–focal] (value in pixels)
focal_value="1536"

# ------ Compute Features parameter ------
# [-m|–describerMethod]
# 	Used method to describe an image:
#		SIFT: (default),
#		AKAZE_FLOAT: AKAZE with floating point descriptors,
#		AKAZE_MLDB: AKAZE with binary descriptors.
describerMethods=("SIFT" "AKAZE_FLOAT")

# [-p|–describerPreset]
#	Used to control the Image_describer configuration:
#		NORMAL,
#		HIGH,
#		ULTRA: !!Can be time consuming!!
describerPresets=("ULTRA")

# ------ Main Compute Matches ------
# [-r|-ratio]
#	(Nearest Neighbor distance ratio, default value is set to 0.8).
#		Using 0.6 is more restrictive => provides less false positive.
ratios=("0.6" "0.8")

# [-g|-geometric_model]
#	type of model used for robust estimation from the photometric putative matches
#		f: Fundamental matrix filtering
#		e: Essential matrix filtering
#		h: Homography matrix filtering
geometric_models=("f" "e" "h")

# [-n|–nearest_matching_method]
#	AUTO: auto choice from regions type,
#	For Scalar based descriptor you can use:
#		BRUTEFORCEL2: BruteForce L2 matching for Scalar based regions descriptor,
#		ANNL2: Approximate Nearest Neighbor L2 matching for Scalar based regions descriptor,
#		CASCADEHASHINGL2: L2 Cascade Hashing matching,
#		FASTCASCADEHASHINGL2: (default).
#			L2 Cascade Hashing with precomputed hashed regions, (faster than CASCADEHASHINGL2 but use more memory).
#	For Binary based descriptor you must use:
#		BRUTEFORCEHAMMING: BruteForce Hamming matching for binary based regions descriptor,
nearest_matching_methods=("BRUTEFORCEL2" "ANNL2" "CASCADEHASHINGL2" "FASTCASCADEHASHINGL2")
```

```
sudo bash mvgmvsMulti.sh
```

Screen tool is recommended to run this script since it's very time consuming.

After process completed. You can see all the outputs are in the "output" folder named with parameters it used.


## Results

I used anteater in UCI as object to reconstruct. And belows are what I got!

### Sparse point cloud model (openMVG)

![sparse point cloud](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/point%20cloud.png)

### Dense point cloud model (openMVS)

![dense point cloud](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/dense%20cloud.png)

### Mesh model (openMVS)

![mesh model](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/mesh.png)

### Refined Mesh model (openMVS)

![refined mesh model](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/refine.png)

### Textured Refined Mesh model (openMVS)

![textured refined mesh model](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/texture.png)


### Final model

![final model](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/modified.png)

### Model built without Mask

![original](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/original.png)

As you can see, the real anteater lies in the red box. It's very small and has very low resolution.



## Built With

+ SSH - Back end Framework
+ BootStrap - Front end Framework


## Author

[@Mark Zhang](https://github.com/Fantastic8)


## Acknowledgments

This project has been supported by UCI MECPS program and advised by professor [@Rainer Dömer](http://www.cecs.uci.edu/~doemer/).

[![UCI MECPS](https://raw.githubusercontent.com/Fantastic8/reconstruction-jetsonnano-realsense/master/media/MECPSLOGO-01-300x85.png)](https://mecps.uci.edu/)