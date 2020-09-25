import pysam
import re
import os
from multiprocessing import Pool

def filter_reads(filename):
    in_bam = pysam.AlignmentFile("./aligned_reads/BAMs/sorted/"+filename, "rb")
    out_bam = pysam.AlignmentFile("./aligned_reads/BAMs/filtered/"+filename, "wb", template=in_bam)
    reads = in_bam.fetch(contig="NR_003278.3",start=1,stop=1869)
    num_reads_filtered = 0
    try:
        for count, read in enumerate(reads):
            #alignment_length = read.query_alignment_length
            MD = read.get_tag("MD")
            if (not re.search("[AGCT][\d^]*[AGCT]", MD) and
                    read.query_alignment_length >= 20 and
                    read.query_alignment_length == read.reference_length):
                out_bam.write(read)
            else:
                num_reads_filtered += 1
    except:
        print(filename)
        raise
    with open("./aligned_reads/BAMs/temp_files/filtering/"+filename+".txt", "w") as file:
        file.write(str(num_reads_filtered)+" of "+str(count+1)+" ("+str(num_reads_filtered/count*100)+"%) filtered.")


file_list = os.listdir("./aligned_reads/BAMs/sorted/")
file_list = list(filter(lambda filename: filename.endswith("bam"), file_list))
assert len(file_list) == 98

p = Pool(90)
try:
    p.map(filter_reads, file_list)
except:
    p.terminate()
    p.close()
    raise
print("done")

path = "./aligned_reads/BAMs/temp_files/filtering/"
file_list = os.listdir(path)
file_list = list(filter(lambda filename: filename.startswith("SRR") and filename.endswith(".txt"), file_list))
assert len(file_list) == 98

for filename in file_list:
    failed = True
    with open(path+filename, "r") as file:
        for line in file.readlines():
            if re.search("\d* of \d* \([0-9.%]*\) filtered.", line):
                failed = False
    if failed:
        print(test, filename)
print("Done.")
