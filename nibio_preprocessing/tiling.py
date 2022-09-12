import argparse
import pdal
import os, glob, shutil
import json
from tqdm import tqdm

from pathlib import Path


class Tiling:
    def __init__(self, input_folder, output_folder, tile_size=10, tile_buffer=0):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.tile_size = tile_size
        self.tile_buffer = tile_buffer
        self.tile_list = []
        self.tile_list_df = None

    def do_tiling_of_single_file(self, file):
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
                { # read input data
                    "filename":file,
                    #"spatialreference":"EPSG:25832" 
                },
                { # defines the tiling processing
                    "type":"filters.splitter", 
                    "length":str(self.tile_size), 
                    "buffer":str(self.tile_buffer) 
                },
                {
                    "type":"writers.las",
                    "filename":file_folder + "/#.las" # the # is a symbol single
                        # placeholder character. If input to the writer consists of multiple PointViews, 
                        #each will be written to a separate file, where the placeholder will be replaced with an incrementing integer. 
                }
            ]
        }
        # do the pdal things
        pipeline = pdal.Pipeline(json.dumps(data))
        pipeline.validate()
        pipeline.execute()
        

    def do_tiling_of_files_in_folder(self):
        
        # create a destination folder for all the tiles
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # get all the files in the input folder
        files = glob.glob(self.input_folder + "/*.laz")

        # loop through all the files
        for file in tqdm(files):
            self.do_tiling_of_single_file(file)


    def run(self):
        self.do_tiling_of_files_in_folder()


def main(input_folder, output_folder, tile_size=10, tile_buffer=0):
    tiling = Tiling(input_folder, output_folder, tile_size, tile_buffer)
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
    args = parser.parse_args()

    main(args.input_folder, args.output_folder, args.tile_size, args.tile_buffer)



 
