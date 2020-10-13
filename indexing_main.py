import utils
import os


filenames = os.listdir("/home/DataShare/eclip_pipeline/20201009_jl_filtered_bam/")
filenames = ["/home/DataShare/eclip_pipeline/20201009_jl_filtered_bam/{filename}".format(filename=filename) for filename in filenames if filename.endswith("_filtered.bam")]

utils.process_files_asynchronously(utils.index_filtered_names, 90, filenames)
