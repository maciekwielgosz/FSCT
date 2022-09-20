#!/bin/bash

# iterate over all the segmented point clouds
for segmented_point_cloud in sample_data/segmented_point_clouds/*.segmented.ply; do
    # get the name of the segmented point cloud
    segmented_point_cloud_name=$(basename $segmented_point_cloud)
    # get the name of the segmented point cloud without the extension
    segmented_point_cloud_name_no_ext="${segmented_point_cloud_name%.*}"
    # create a directory for the instance segmented point clouds
    mkdir -p sample_data/instance_segmented_point_clouds/$segmented_point_cloud_name_no_ext
    # iterate over all the tiles of the segmented point cloud
    for tile in sample_data/segmented_point_clouds/tiled/$segmented_point_cloud_name_no_ext/*.ply; do
        # get the name of the tile
        tile_name=$(basename $tile)
        # get the name of the tile without the extension
        tile_name_no_ext="${tile_name%.*}"
        echo "Processing $tile"
        # show the output folder
        echo "Output folder: sample_data/instance_segmented_point_clouds/$segmented_point_cloud_name_no_ext/$tile_name_no_ext"

        python3 fsct/points2trees.py \
        -t $tile \
        --tindex sample_data/segmented_point_clouds/tiled/$segmented_point_cloud_name_no_ext/tile_index.dat \
        -o sample_data/instance_segmented_point_clouds/$segmented_point_cloud_name_no_ext/$tile_name_no_ext \
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



