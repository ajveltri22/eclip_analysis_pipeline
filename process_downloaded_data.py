from utils import FunctionWrapperAddQueue
from subprocess import run, PIPE, STDOUT
import os
import logging

@FunctionWrapperAddQueue()
def gunzip_file(filepath):
    p = run(["gzip", "-d", filepath], stdout=PIPE, stderr=STDOUT)
    return p.stdout.decode("utf-8")

@FunctionWrapperAddQueue()
def trim_reads(filepath_mate1, filepath_mate2, outpath_mate1, outpath_mate2):
    p = run([
        "bbduk.sh",
        "in="+filepath_mate1,
        "in2="+filepath_mate2,
        "out="+outpath_mate1,
        "out2="+outpath_mate2,
        "literal=AGATCGGAAGAGCACACGTCTGAACTCCAGTCA,AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT,AACTTGTAGATCGGAAGA",
        "k=33", # this parameter sets the minimum kmer being trimmed.
                              #Longer = more specific, shorter = more sensitive
        "mink=15", #includes truncations of the kmers down to 8
        "mm=f", #do not ignore middle base mismatch of kmer
        "rcomp=t", #do not allow reverse complement kmer matches
        "copyundefined=t",
        "ktrim=r",
        #"forcetrimleft=12", #removes random barcode on left of reads. FUCK shouldn't have done this
        "minavgquality=10",
        "minlength=10",
        "threads="+"1",
        "overwrite=t",
        "t=1", #prevents each instance from using more than one thread.)
    ], stdout=PIPE, stderr=STDOUT)
    return p.stdout.decode("utf-8")

@FunctionWrapperAddQueue()
def align_reads(outsam_path, filepaths_mate1, filepaths_mate2):
    p = run([
        "hisat2",
        "-p", "1",
        "-x", "./hisat2_index_hsrRNA/",
        "-1", ",".join(filepaths_mate1),
        "-2", ",".join(filepaths_mate2),
        "-k", "1",
        "-S", outsam_path
    ], stdout=PIPE, stder=STDOUT)
    return p.stdout.decode("utf-8")

@FunctionWrapperAddQueue()
def sam_to_bam(in_sam_filepath, out_bam_filepath):
    p = run([
        "samtools", "view",
        "-b",
        "-q", "1",
        "-o", out_bam_filepath,
        in_sam_filepath
    ], stdout=PIPE, stderr=STDOUT)
    return p.stdout.decode("utf-8")

@FunctionWrapperAddQueue()
def sort_bam(in_bam_filepath, out_bam_filepath):
    p = run([
        "samtools", "sort",
        "-o", out_bam_filepath,
        in_bam_filepath,
    ], stdout=PIPE, stderr=STDOUT)
    return p.stdout.decode("utf-8")

@FunctionWrapperAddQueue()
def index_bam(in_bam_filepath):
    p = run([
        "samtools", "index",
        in_bam_filepath,
    ], stdout=PIPE, stderr=STDOUT)
    return p.stdout.decode("utf-8")

@FunctionWrapperAddQueue()
def convert_sort_index(in_sam_filepath, temporary_directory_path):
    logger = logging.getLogger()
    if not in_sam_filepath.endswith(".sam"):
        logger.error(f"Error in converting SAM to BAM. {in_sam_filepath} does not have a .sam extension.")
        raise Exception("Attempting to convert a file without .sam extension!")
    filename = os.path.split(in_sam_filepath)[1].strip(".sam")

    stdout_dir_path = os.path.join(temporary_directory_path, "convert_sort_index_STDOUT")
    os.mkdir(os.path.join(temporary_directory_path, "unsorted_bam"))
    os.mkdir(os.path.join(temporary_directory_path, "sorted_bam"))
    os.mkdir(stdout_dir_path)
    unsorted_bam_filepath = os.path.join(temporary_directory_path, "unsorted_bam", f"{filename}.bam")
    sorted_bam_filepath = os.path.join(temporary_directory_path, "sorted_bam", f"{filename}_sorted.bam")


    sam_to_bam_stdout = sam_to_bam(in_sam_filepath, unsorted_bam_filepath)
    sort_bam_stdout = sort_bam(unsorted_bam_filepath, sorted_bam_filepath)
    index_bam_stout = index_bam(sorted_bam_filepath)

    stdout_file_path = os.path.join(stdout_dir_path, f"{filename}_csi_STDOUT.txt")
    with open(stdout_file_path, "w") as stdout_file:
        stdout_file.write("CONVERTING"+"="*10+
                          f"\n{sam_to_bam_stdout}\n\n"+
                          "SORTING"+"="*10+
                          f"\n{sort_bam_stdout}\n\n"+
                          "INDEXING" + "=" * 10 +
                          f"\n{index_bam_stout}\n\n")

    logger.log(f"Finished convert_sort_index, wrote STDOUT to {stdout_file_path}")
