import time
from multiprocessing import Pool, Manager
from functools import wraps


def yn_input(message):
    """

    :param message:
    :return:
    """
    while True:
        y_or_n = input("{} [y/n] ".format(message))
        yn_tf_mapper = {"y": True, "n": False}
        if y_or_n in ["y", "n"]:
            return yn_tf_mapper[y_or_n]
        else:
            print("Answer 'y' or 'n'")


class FunctionWrapperAddQueue:
    """
    Used as a decorator for functions, adding a queue object as the
    last positional argument. This allows the wrapped function to report
    on its doneness to the queue in real time.
    """

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            output = func(*args[0][:-1], **kwargs)
            if hasattr(args[0][-1], "put"):  # better way to check if the last argument is a Queue?
                args[0][-1].put(True)
            return output

        return wrapper


''' Toy example function for testing
@FunctionWrapperAddQueue()
def myfunc(count_to):
    for i in range(count_to+1):
        print(f"{i} of {count_to}")
        time.sleep(.5)
    return(f"I counted to {count_to}")
'''


def process_files_asynchronously(func, num_cores, *args):
    """
    Starts multiprocessing for a particular function, taking a list of arguments to be passed to
    the function one at a time in each thread. The function should accept a queue as its final argument
    to allow progress reporting. Intended to be used with functions wrapped by utils.FunctionWrapperAddQueue()
    :param func:
    :param num_cores:
    :param args:
    :return:
    """
    p = Pool(num_cores)
    m = Manager()
    q = m.Queue()
    arg_list = list(*args)
    in_args = list(zip(arg_list, [q] * len(arg_list)))
    result = p.map_async(func, in_args)
    while not result.ready():
        print("\rRunning... {}/{}".format(str(q.qsize()), len(arg_list)), end="")
        time.sleep(1)
    p.close()
    print("\rDone. {}/{} processed.".format(str(q.qsize()), len(arg_list)))
    return result.get()

def extract_contig_names(fasta_filepath):
    # Obtain the first line of a FastA file
    file = open(fasta_filepath, "r")
    fasta_list = []

    for line in file.readlines():
        if line.startswith(">"):
            new_line=line[1:].strip()
            line_list=new_line.split()
            first_word=line_list[0]
            fasta_list.append(first_word)
    file.close()
    return fasta_list

from subprocess import Popen


def index_filtered_names(filepath):
    #Split up the filepath to get the name of the file and the directory where it is located.
    #This information will be used to set up a logfile in the same directory, with the filename
    path_parts = filepath.split("/")
    file_name = path_parts[-1]
    file_directory = filepath.strip(file_name)

    logname= file_directory + "/log." + file_name
    p = Popen(["samtools", "index", filepath], stderr=open(logname, "w"), stdout=open(logname, "w"))
    p.wait()
