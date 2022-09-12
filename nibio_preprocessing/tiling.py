import argparse
import pdal
import os, glob, shutil
import json
from tqdm import tqdm

from pathlib import Path


class Tiling:
    """
    The tiling operation on las files is done by the pdal splitter filter.
    """
    def __init__(self, input_folder, output_folder, tile_size=10, tile_buffer=0, do_mapping_to_ply=False):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.output_folder_ply = output_folder + "_ply"
        self.tile_size = tile_size
        self.tile_buffer = tile_buffer
        self.do_mapping_to_ply = do_mapping_to_ply
 

    def do_tiling_of_single_file(self, file):
        """
        This function will tile a single file into smaller files
        """

        # get a name for the file 
        file_name_base = os.path.basename(file)
        file_name = os.path.splitext(file_name_base)[0]

        # create a folder for the file
        file_folder = os.path.join(self.output_folder, file_name)
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)

        # create a pipeline for the file
        data = {
            "pipeline":[
                { 
                    "filename":file,
                    #"spatialreference":"EPSG:25832" 
                },
                { 
                    "type":"filters.splitter", 
                    "length":str(self.tile_size), 
                    "buffer":str(self.tile_buffer) 
                },
                {
                    "type":"writers.las",
                    "filename":file_folder + "/#.las" 
                  
                }
            ]
        }
        # do the pdal things
        pipeline = pdal.Pipeline(json.dumps(data))
        pipeline.validate()
        pipeline.execute()

        # convert the tiles to ply
        if self.do_mapping_to_ply:
            self.convert_files_in_folder_from_las_to_ply(file_folder)
        

    def do_tiling_of_files_in_folder(self):
        """
        This function will tile all the files in a folder
        """
        
        # create a destination folder for all the tiles
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # get all the files in the input folder
        files = glob.glob(self.input_folder + "/*.laz")

        # loop through all the files
        for file in tqdm(files):
            self.do_tiling_of_single_file(file)

    def convert_single_file_from_las_to_ply(self, file):
        """
        This function will convert a single file from las to ply
        """

        # get a name for the file 
        file_name_base = os.path.splitext(file)[0]

        # create a pipeline for the file
        data = {
            "pipeline":[
                { # read input data
                    "type":"readers.las",
                    "filename":file,
                    #"spatialreference":"EPSG:25832" 
                },
                {
                    "type":"writers.ply",
                    "filename":file_name_base +".ply" 
                }
            ]
        }
        # do the pdal things
        pipeline = pdal.Pipeline(json.dumps(data))
        pipeline.execute()

    def convert_files_in_folder_from_las_to_ply(self, folder=None):
        """
        This function will convert all the files in a folder from las to ply
        """

        # get all the files in the folder and subfolders
        files = glob.glob(folder + "/*.las")

        # loop through all the files
        for file in tqdm(files):
            self.convert_single_file_from_las_to_ply(file)

    def get_tile_index(self):
        pass

    def run(self):
        self.do_tiling_of_files_in_folder()

def main(input_folder, output_folder, tile_size=10, tile_buffer=0, do_mapping_to_ply=False):
    """
    This function will tile all the files in a folder
    """
    tiling = Tiling(input_folder, output_folder, tile_size, tile_buffer, do_mapping_to_ply)
    tiling.run()


if __name__ == "__main__":
    # read command line arguments
    parser = argparse.ArgumentParser(description="Tiling")
    parser.add_argument(
        "-i",
        "--input_folder",
        type=str,
        help="Input folder containing las files",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        type=str,
        help="Output folder containing las files",
        required=True,
    )   
    parser.add_argument(
        "-t",
        "--tile_size",
        type=int,
        help="Tile size in meters",
        required=False,
        default=10,
    )
    parser.add_argument(
        "-b",
        "--tile_buffer",
        type=int,
        help="Tile buffer in meters",
        required=False,
        default=0,
    )
    parser.add_argument(
        "-m",
        "--do_mapping_to_ply",
        type=bool,
        help="Do mapping to ply",
        required=False,
        default=True,
    )

    args = parser.parse_args()

    main(args.input_folder, args.output_folder, args.tile_size, args.tile_buffer, args.do_mapping_to_ply)



 
