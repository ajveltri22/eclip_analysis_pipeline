#!/usr/bin/env python3


import argparse
import encode_downloader
import utils
import os
import logging
import process_downloaded_data


def main(args):

    #DOWNLOAD ENCODE DATA
    if not os.access(args.working_directory, os.W_OK):
        raise FileNotFoundError("Working directory does not exist or is write protected!")
    os.chdir(args.working_directory)
    os.makedirs("./logs/pipeline/", exist_ok=True)
    logging.basicConfig(filename="./logs/pipeline/pipeline.log", format='%(asctime)s %(message)s', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    encode_experiment_accessions = args.accessions_file.readlines()
    file_table, bad_file_size_accs = encode_downloader.main(args.num_cores, encode_experiment_accessions, args.working_directory)
    num_bad_files = len(bad_file_size_accs)
    if num_bad_files > 0:
        logger.warning(f"{num_bad_files} files don't match the expected size.")
        if utils.yn_input(f"Do you want to continue despite potential download errors?"):
            logger.info(f"User chose to continue despite {num_bad_files} potential download errors.")
        else:
            raise KeyboardInterrupt

    #UNZIP DOWNLOADED ENCODE FILES
    os.makedirs("./logs/decompressing/", exist_ok=True)
    os.makedirs("./logs/trimming/", exist_ok=True)






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="eCLIP data processing pipeline")
    parser.add_argument("num_cores", action="store", type=int)
    parser.add_argument("accessions_file", action="store", type=argparse.FileType("r"),
                        help="A file containing ENCODE accessions for data to analyze")
    parser.add_argument("working_directory", action="store", type=str,
                        help="The directory where this pipeline will download and process data")
    args = parser.parse_args()
    main(args)
