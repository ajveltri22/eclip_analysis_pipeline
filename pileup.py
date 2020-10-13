import pysam
import os
import re
import threading
from multiprocessing import Pool
import pandas as pd
import numpy as np
import pickle

'''ANTHONY'S IPYNB CODE

# get list of total reads
path = "./logs/alignment/" #"./aligned_reads/BAMs/temp_files/filtering/"
file_list = os.listdir(path)
#file_list = list(filter(lambda filename: filename.endswith("bam.txt"), file_list))
file_list = list(filter(lambda filename: filename.endswith("stderr.txt"), file_list))
#assert len(file_list) == 98

num_reads_dict = {}
for filename in file_list:
    finished = False
    with open(path+filename, "r") as file:
        for line in file.readlines():
            match = re.search("^(\d*) reads; of these:", line) #3634 of 2979650 (0.121960632960247%) filtered.
            #match = re.search("^(\d*) of (\d*) \([0-9.%]*\) filtered.", line)
            if match:
                num_reads_dict[filename.split(".")[0]] = int(match.group(1))
                #num_reads_dict[filename.split("_")[0]] = int(match.group(2)) - int(match.group(1))
                finished = True
                continue
    if not finished:
        print(filename, "did not finish.")

print("Done")


def get_pileup(file_path):
    global num_reads_dict
    samfile = pysam.AlignmentFile(file_path, "rb")

    sample_name = re.search("(ENCSR[0-9A-Z])_", file_path).group(1)
    pos_depth_list = pd.DataFrame([*samfile.count_coverage("NR_003278.3", 0, 1870, quality_threshold=0)]).sum().T
    if len(pos_depth_list) != 0:
        pos_depth_list = pos_depth_list / num_reads_dict[sample_name] * 10 ** 6
    else:
        pos_depth_list = pd.Series()
    return (sample_name, pos_depth_list)

path = "./aligned_reads/BAMs/filtered/"
file_list = os.listdir(path)
file_list = list(filter(lambda filename: filename.endswith(".bam"), file_list))
path_file_list = [path+filename for filename in file_list]
assert len(file_list) == 98

p = Pool(90)
try:
    map_list = p.map(get_pileup, path_file_list)
except:
    p.terminate()
    p.close()
    raise

map_unzip = list(zip(*map_list))
pileup_data = pd.concat(map_unzip[1], axis=1)
pileup_data.columns = map_unzip[0]
pileup_data.fillna(0, inplace=True)

'''