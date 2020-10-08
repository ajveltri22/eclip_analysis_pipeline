import pysam
import random

def compare_bam(filename1, filename2):
    one_bam = pysam.AlignmentFile(filename1, "rb")
    two_bam = pysam.AlignmentFile(filename2,"rb")
    one_bam_list = []
    two_bam_list = []
    one_bam_count = 0
    two_bam_count = 0
    for read in one_bam:
        one_bam_count += 1
        one_bam_list.append(read.query_name)
    for read in two_bam:
        two_bam_count += 1
        two_bam_list.append(read.query_name)
    print('----------')
    print('Length of file1: ' + str(one_bam_count))
    print('Length of file2: ' + str(two_bam_count))
    print('Difference between file1 and file2: ' + str(one_bam_count- two_bam_count))
    print(len(set(one_bam_list).difference(two_bam_list)))

def generate_random_bam(input_filepath):
    input_file = pysam.AlignmentFile(input_filepath, "rb")
    output_filepath = input_filepath.replace('.bam','_RANDOM.bam')
    output_file = pysam.AlignmentFile(output_filepath, "wb", template=input_file)

    for read in input_file:
        random_number = random.randint(1,3)
        if random_number == 2:
            output_file.write(read)
        else:
            continue


one = "/Users/lij/PycharmProjects/eclip_analysis_pipeline/filtered_examples/JL_test_output/SRR9693961_aligned_sorted_filtered.bam"
two = "/Users/lij/PycharmProjects/eclip_analysis_pipeline/filtered_examples/filtered/SRR9693961_aligned_sorted_filtered.bam"
random_one = "/Users/lij/PycharmProjects/eclip_analysis_pipeline/filtered_examples/JL_test_output/SRR9693961_aligned_sorted_filtered_RANDOM.bam"

# generate_random_bam(one)

compare_bam(two,one)
print('--------')
compare_bam(one,two)