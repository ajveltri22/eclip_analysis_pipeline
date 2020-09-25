import pysam
import re
import os
from multiprocessing import Pool, cpu_count
from itertools import product

def filter_reads(filename, output_dir):
    '''Given an input .bam filename and a output directory path, filters reads for a minimum alignment length of 20 and
    no gaps. This function is mostly a helper function to be called in mp_filter_reads()'''
    #Check that the input filename is a .bam file, and that the output_dir is correctly formatted
    assert filename.endswith('.bam') and output_dir.endswith('/')
    in_bam = pysam.AlignmentFile("./aligned_reads/BAMs/sorted/"+filename, "rb")

    #Adds _filtered suffix to output .bam file
    output_filename = filename.replace('.bam','_filtered.bam')
    out_bam = pysam.AlignmentFile(output_dir+output_filename, "wb", template=in_bam)

    #Fetch all reads aligned to given contig
    reads = in_bam.fetch(contig="NR_003278.3", start=1, stop=1869)
    num_reads_filtered = 0

    #Iterate through reads and write out filtered reads to output .bam file
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

    #Generate run log
    with open("./aligned_reads/BAMs/temp_files/filtering/"+filename+".txt", "w") as file:
        file.write(str(num_reads_filtered)+" of "+str(count+1)+" ("+str(num_reads_filtered/count*100)+"%) filtered.")

def mp_filter_reads(input_dir, output_dir):
    '''Sets up a multiprocessing Pool to call the filter_reads() function on an input_dir path containing a number of sorted .bam files'''

    #Generate list of filenames in the input directory
    file_list = os.listdir(input_dir)
    # file_list = os.listdir("./aligned_reads/BAMs/sorted/")
    file_list = list(filter(lambda filename: filename.endswith("bam"), file_list))

    #Spawn a multiprocessing pool of worker processes based on cpu count
    print('Using ' + str(cpu_count()-1) + ' cores')
    p = Pool(cpu_count()-1)

    #Generate argument tuples to pass into p.starmap
    #Ex. (filename1, output_dir), (filename2, output_dir), etc.
    #Output_dir is passed into a single-item tuple to prevent itertools.product() from iterating over the character
    output_dir_dummy_tuple = (output_dir,)
    starmap_file_list = product(file_list, output_dir_dummy_tuple)

    #Uses p.starmap() instead of p.map() to allow multiple arguments in the multiprocessed function.
    try:
        p.starmap(filter_reads, starmap_file_list)
    except:
        p.terminate()
        p.close()
        raise
    print("Done filtering reads for all sorted .bam files in " + input_dir)

def check_filter_logs(input_dir="./aligned_reads/BAMs/temp_files/filtering/"):
    # path = "./aligned_reads/BAMs/temp_files/filtering/"

    # Generate list of filenames in the input directory
    file_list = os.listdir(input_dir)
    file_list = list(filter(lambda filename: filename.startswith("SRR") and filename.endswith(".txt"), file_list))

    for filename in file_list:
        failed = True
        with open(input_dir+filename, "r") as file:
            for line in file.readlines():
                if re.search("\d* of \d* \([0-9.%]*\) filtered.", line):
                    failed = False
        if failed:
            print(line, filename)
    print("Done.")