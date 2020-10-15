from utils import FunctionWrapperAddQueue
from subprocess import run, PIPE, STDOUT

@FunctionWrapperAddQueue()
def gunzip_file(filepath):
    p = run(["gzip", "-d", filepath], stdout=PIPE, stderr=STDOUT)
    return p.stdout

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
    return p.stdout

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
    return p.stdout

