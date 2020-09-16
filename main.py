#!/usr/bin/env python3
"""TODO:
 - reconfigure main() to accept arguments in a better way, rather than accepting the argparse namespace object.
 - Implement way to skip downloading files if they're already there.
"""

import argparse
import encode_downloader
import utils
import os
import logging
import sys
import process_downloaded_data


def main(args):
    # DOWNLOAD ENCODE DATA
    if not os.access(args.working_directory, os.W_OK):
        raise FileNotFoundError("Working directory does not exist or is write protected!")
    os.chdir(args.working_directory)
    os.makedirs("./logs/pipeline/", exist_ok=True)
    logging.basicConfig(filename="./logs/pipeline/pipeline.log", format='%(asctime)s [%(threadName)-12.12s] [%('
                                                                        'levelname)s] %(message)s ',
                        level=logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s ')
    stderr_handler = logging.StreamHandler(sys.stdout)
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.INFO)
    logger.addHandler(stderr_handler)
    encode_experiment_accessions = [acc.strip() for acc in args.accessions_file.readlines()]
    file_table, bad_file_size_accs = encode_downloader.main(args.num_cores, encode_experiment_accessions,
                                                            args.working_directory)
    num_bad_files = len(bad_file_size_accs)
    if num_bad_files > 0:
        logger.warning(f"{num_bad_files} files don't match the expected size.")
        if utils.yn_input(f"Do you want to continue despite potential download errors?"):
            logger.info(f"User chose to continue despite {num_bad_files} potential download errors.")
        else:
            raise KeyboardInterrupt

    # UNZIP DOWNLOADED ENCODE FILES
    os.makedirs("./logs/decompressing/", exist_ok=True)
    os.makedirs("./logs/trimming/", exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="eCLIP data processing pipeline")
    parser.add_argument("num_cores", action="store", type=int)
    parser.add_argument("accessions_file", action="store", type=argparse.FileType("r"),
                        help="A file containing ENCODE accessions for data to analyze")
    parser.add_argument("working_directory", action="store", type=str,
                        help="The directory where this pipeline will download and process data")
    parser.add_argument("working_directory", action="store", type=str,
                        help="The directory where this pipeline will download and process data")
    args = parser.parse_args()
    main(args)
