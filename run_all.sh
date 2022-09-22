#!/bin/bash

############################ paramters #################################################
# General parameters
CLEAR_INPUT_FOLDER=1  # 1: clear input folder, 0: not clear input folder

# Tiling parameters
N_TILES=3
SLICE_THICKNESS=0.5
FIND_STEMS_HEIGHT=2
FIND_STEMS_THICKNESS=0.5
GRAPH_MAXIMUM_CUMULATIVE_GAP=3
ADD_LEAVES_VOXEL_LENGTH=0.5
############################# end of parameters declaration ############################


# Do the environment setup
# export PYTHONPATH='.'
# conda activate pdal-env-1

# read input folder as a command line argument
# show a message to provide the input folder
data_folder=$1

# if no input folder is provided, case a message and exit
if [ -z "$data_folder" ]
then
    echo "No input folder provided, please provide the input folder as a command line argument"
    exit 1
fi

# clear input folder if CLEAR_INPUT_FOLDER is set to 1
if [ $CLEAR_INPUT_FOLDER -eq 1 ]
then
    # delete all the files and folders except the ply files in the input folder
    echo "Clearing input folder"
    find $data_folder/ -type f ! -name '*.ply' -delete # delete all the files except the ply files
    find $data_folder/* -type d -exec rm -rf {} + # delete all the folders in the input folder
fi

# # iterate over all files in the input folder and do sematic segmentation
echo  "Starting semantic segmentation"
for file in $data_folder/*.ply; do
    python fsct/run.py --point-cloud $file --batch_size 5 --odir $data_folder
done

# move the output of the first step to the input folder of the second step
mkdir -p $data_folder/segmented_point_clouds

# Check if the file exists and if they exist move them to the new folder
if [ -f "$data_folder/*.ply" ]
then
    mv $data_folder/*.ply $data_folder/segmented_point_clouds
fi

mv $data_folder/*.segmented.ply $data_folder/segmented_point_clouds

# do the tiling and tile index generation
echo "Tiling and tile index generation"
python nibio_preprocessing/tiling.py -i $data_folder/segmented_point_clouds/ -o $data_folder/segmented_point_clouds/tiled

#  iterate over all the segmented point clouds
check if the output folder exists

mkdir -p $data_folder/instance_segmented_point_clouds

# Do the instances and iterate over all the segmented point clouds
for segmented_point_cloud in data_folder/segmented_point_clouds/*.segmented.ply; do
    # get the name of the segmented point cloud
    segmented_point_cloud_name=$(basename $segmented_point_cloud)
    # get the name of the segmented point cloud without the extension
    segmented_point_cloud_name_no_ext="${segmented_point_cloud_name%.*}"
    # create a directory for the instance segmented point clouds
    mkdir -p data_folder/instance_segmented_point_clouds/$segmented_point_cloud_name_no_ext
    # iterate over all the tiles of the segmented point cloud
    for tile in data_folder/segmented_point_clouds/tiled/$segmented_point_cloud_name_no_ext/*.ply; do
        # get the name of the tile
        tile_name=$(basename $tile)
        # get the name of the tile without the extension
        tile_name_no_ext="${tile_name%.*}"
        echo "Processing $tile"
        # show the output folder
        echo "Output folder: $data_folder/instance_segmented_point_clouds/$segmented_point_cloud_name_no_ext/$tile_name_no_ext"
        python3 fsct/points2trees.py \
        -t $tile \
        --tindex $data_folder/segmented_point_clouds/tiled/$segmented_point_cloud_name_no_ext/tile_index.dat \
        -o $data_folder/instance_segmented_point_clouds/$segmented_point_cloud_name_no_ext/$tile_name_no_ext \
        --n-tiles 3 \
        --slice-thickness .5 \
        --find-stems-height 2 \
        --find-stems-thickness .5 \
        --pandarallel --verbose \
        --add-leaves \
        --add-leaves-voxel-length .5 \
        --graph-maximum-cumulative-gap 3 \
        --save-diameter-class \
        --ignore-missing-tiles
    done
done

# do merging of the instance segmented point clouds
echo "Merging instance segmented point clouds"
python nibio_preprocessing/merging_and_labeling.py --data_folder $data_folder/instance_segmented_point_clouds/ 



