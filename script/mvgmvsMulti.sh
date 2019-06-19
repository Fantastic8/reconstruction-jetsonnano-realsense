#!/bin/sh

#@author Mark Zhang
#@create May 26, 2019

# To run this script you MUST have the followings under same directory:
# Folder: images (containing images of object you want to reconstruct)
# File: mvgmvs.sh

# ------ Parameters ------

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

# check
if [ ! -d "images" ];then
	echo "images folder not found"
	exit 1
fi

if [ ! -f "mvgmvs.sh" ];then
	echo "mvgmvs.sh file not exits"
	exit 1
fi


current_location=`pwd`
totalStep=`expr ${#describerMethods[@]} \* ${#describerPresets[@]} \* ${#ratios[@]} \* ${#geometric_models[@]} \* ${#nearest_matching_methods[@]}`
countStep=0
# Main
echo "Total Steps: ${totalStep}"
echo ""
mkdir output
for describerMethod_value in "${describerMethods[@]}"
do
	for describerPreset_value in "${describerPresets[@]}"
	do
		for ratio_value in "${ratios[@]}"
		do
			for geometric_model_value in "${geometric_models[@]}"
			do
				for nearest_matching_method_value in "${nearest_matching_methods[@]}"
				do
					subdir="${focal_value}_${describerMethod_value}_${describerPreset_value}_${ratio_value}_${geometric_model_value}_${nearest_matching_method_value}"
					echo ""
					echo "------ $subdir ------"
					mkdir $subdir
					ln -s $current_location/images $current_location/$subdir/images
					cp $current_location/mvgmvs.sh $current_location/$subdir/mvgmvs.sh
					cd $subdir
					output=`sh mvgmvs.sh $focal_value $describerMethod_value $describerPreset_value $ratio_value $geometric_model_value $nearest_matching_method_value`
					echo "Done"
					cd ..

					# Check output files and collect outputs
					if [ ! -f "${subdir}/scene_dense_mesh_refine_texture.ply" ];then
						# no output files! Delete whole folder
						echo "Reconstruct Failed"
						rm -rf "${subdir}"
					else
						# collect outputs
						mkdir "output/${subdir}"
						mv "${subdir}/out_Incremental_Reconstruction/cloud_and_poses.ply" "output/${subdir}/"
						mv "${subdir}/scene_dense.ply" "output/${subdir}/"
						mv "${subdir}/scene_dense_mesh.ply" "output/${subdir}/"
						mv "${subdir}/scene_dense_mesh_refine.ply" "output/${subdir}/"
						mv "${subdir}/scene_dense_mesh_refine_texture.ply" "output/${subdir}/"
						mv "${subdir}/scene_dense_mesh_refine_texture.png" "output/${subdir}/"
						mv "${subdir}/mvgmvs.log" "output/${subdir}/"
					fi

					# count steps
					countStep=`expr ${countStep} + 1`
					echo "... ${countStep}/${totalStep}"
				done
			done
		done
	done
done