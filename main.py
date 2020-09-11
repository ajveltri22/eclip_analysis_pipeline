#!/usr/bin/env python3


import argparse
import encode_downloader
import utils

def main():

    encode_experiment_accessions = args.accessions_file.readlines()
    file_table, bad_file_size_accs = encode_downloader.main(args.num_cores, encode_experiment_accessions)

    if len(bad_file_size_accs) < 0:
        if not utils.yn_input("Do you want to continue despite incorrect files?"):
            raise KeyboardInterrupt
            y_or_n = input("Do you want to continue despite incorrect files? (y/n)")








if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eclip data processing pipeline")
    parser.add_argument("num_cores", action="store", type=int)
    parser.add_argument("accessions_file", action="store", type=argparse.FileType("r"), help="A file containing ENCODE accessions for data to analyze")

    args = parser.parse_args()

    main()


