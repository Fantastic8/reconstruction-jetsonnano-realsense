#!/bin/sh

# To run this script you MUST have the followings under same directory:
# Folder: images (containing images of object you want to reconstruct)

# ------ Image Listing parameter ------
# [-f|–focal] (value in pixels)
#focal="1536"
focal=$1


# ------ Compute Features parameter ------
# [-m|–describerMethod]
# 	Used method to describe an image:
#		SIFT: (default),
#		AKAZE_FLOAT: AKAZE with floating point descriptors,
#		AKAZE_MLDB: AKAZE with binary descriptors.
#describerMethod=""
describerMethod=$2

# [-p|–describerPreset]
#	Used to control the Image_describer configuration:
#		NORMAL,
#		HIGH,
#		ULTRA: !!Can be time consuming!!
#describerPreset="NORMAL"
describerPreset=$3

# ------ Main Compute Matches ------
# [-r|-ratio]
#	(Nearest Neighbor distance ratio, default value is set to 0.8).
#		Using 0.6 is more restrictive => provides less false positive.
#ratio=""
ratio=$4

# [-g|-geometric_model]
#	type of model used for robust estimation from the photometric putative matches
#		f: Fundamental matrix filtering
#		e: Essential matrix filtering
#		h: Homography matrix filtering
#geometric_model=""
geometric_model=$5

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
#nearest_matching_method=""
nearest_matching_method=$6


# ------ Initialize Parameters ------
if [ -n "$focal" ]; 
then
  focal="-f $focal"
fi

if [ -n "$describerMethod" ]; 
then
  describerMethod="-m $describerMethod"
fi

if [ -n "$describerPreset" ]; 
then
  describerPreset="-p $describerPreset"
fi

if [ -n "$ratio" ]; 
then
  ratio="-r $ratio"
fi

if [ -n "$geometric_model" ]; 
then
  geometric_model="-g $geometric_model"
fi

if [ -n "$nearest_matching_method" ]; 
then
  nearest_matching_method="-n $nearest_matching_method"
fi


start_time=`date --date='0 days ago' "+%Y-%m-%d %H:%M:%S"`

echo ""
echo "========== Description =========="
echo "openMVG"
echo "	Image Listing: $focal"
echo "	Compute Features: $describerPreset $describerMethod"
echo "	Compute Matches: $ratio $geometric_model $nearest_matching_method"
echo ""

echo ""
echo "========== Description ==========">>mvgmvs.log
echo "openMVG">>mvgmvs.log
echo "	Image Listing: $focal">>mvgmvs.log
echo "	Compute Features: $describerPreset $describerMethod">>mvgmvs.log
echo "	Compute Matches: $ratio $geometric_model $nearest_matching_method">>mvgmvs.log
echo "">>mvgmvs.log

echo "----- openMVG -----"
echo "Image Listing ...\c"
output=`openMVG_main_SfMInit_ImageListing -d /root/openMVG/src/openMVG/exif/sensor_width_database/sensor_width_camera_database.txt -i images/ -o matches/ $focal 1>>mvgmvs.log 2>&1`
echo " Done"
echo "Compute Features ...\c"
output=`openMVG_main_ComputeFeatures -i matches/sfm_data.json -o matches $describerPreset $describerMethod 1>>mvgmvs.log 2>&1`
echo " Done"
echo "Compute Matches ...\c"
output=`openMVG_main_ComputeMatches -i matches/sfm_data.json -o matches $ratio $geometric_model $nearest_matching_method 1>>mvgmvs.log 2>&1`
echo " Done"
echo "Incremental SFM ...\c"
output=`openMVG_main_IncrementalSfM -i matches/sfm_data.json -m matches -o out_Incremental_Reconstruction 1>>mvgmvs.log 2>&1`
echo " Done"

echo ""
echo "----- oepnMVS -----"
echo "openMVG -> openMVS ...\c"
output=`openMVG_main_openMVG2openMVS -i out_Incremental_Reconstruction/sfm_data.bin -o scene.mvs 1>>mvgmvs.log 2>&1`
echo " Done"
echo "Densify Point Cloud ...\c"
output=`DensifyPointCloud scene.mvs 1>>mvgmvs.log 2>&1`
echo " Done"
echo "Reconstruct Mesh ...\c"
output=`ReconstructMesh scene_dense.mvs 1>>mvgmvs.log 2>&1`
echo " Done"
echo "Refine Mesh ...\c"
output=`RefineMesh scene_dense_mesh.mvs --max-face-area 16 1>>mvgmvs.log 2>&1`
echo " Done"
echo "Texture Mesh ...\c"
output=`TextureMesh scene_dense_mesh_refine.mvs 1>>mvgmvs.log 2>&1`
echo " Done"
finish_time=`date --date='0 days ago' "+%Y-%m-%d %H:%M:%S"`
duration=$(($(($(date +%s -d "$finish_time")-$(date +%s -d "$start_time")))))
echo "this shell script execution duration: $duration"
echo "this shell script execution duration: $duration">>mvgmvs.log
