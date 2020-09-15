#!/usr/bin/env python3

import requests
import os
import pandas as pd
from functools import reduce
from multiprocessing import Pool, Manager
from warnings import warn
from time import time

import utils


class EncodeExperimentDownloader:
    """
    This class constitutes a downloader for the FASTQ files associated with
    a particular ENCODE eCLIP experiment accession (and corresponding controls).
    Arguments are a string of the ENCODE experiment accession and an optional
    manager queue for multithreading. Initializing the class creates a folder
    architecture like so uses the ENCODE REST API to get information about the
    experiments and create a folder architecture like so:
        ./fastq/
            {cell_line}/
                {accession}_{target}/
                    {eclip_or_control}/
                        {accession}_{target}_rep{n}/
    The number of files to download and total space required are calculated and
    stored in self.num_files and self.total_download_size, respectively.
    Download will not begin until the download_fastqs method is called. The FASTQ
    files will then be downloaded to the appropriate folder with the filename:
                {accession}_{target}_rep{n}_mate{n}.fastq.gz

    TODO:
    - download barcode for trimming??
    - create txt file with metadata??
    """

    def __init__(self, eclip_encode_accession, queue=None):
        self.eclip_acc = eclip_encode_accession
        self.eclip_json = self.get_json(self.eclip_acc)
        self.get_properties_from_json(self.eclip_json)
        self.create_folder_heirarchy()
        self.file_info_table = {
            "file_accession": [],
            "file_path": [],
            "replicate": [],
            "mate": [],
            "mate_accession": [],
            "experiment_accession": [],
            "target": [],
            "cell_line": [],
            "eclip_experiment_accession": [],
            "experiment_type": [],
            "url": [],
            "file_size": [],
            "barcode_id": [],
            "barcode_sequence": [],
        }
        self.create_table()
        if queue is not None:
            queue.put(self.eclip_acc)

    def get_json(self, encode_exp_accession):
        url = 'https://www.encodeproject.org/experiments/{acc}/'.format(acc=encode_exp_accession)
        response = requests.get(url, headers={'accept': 'application/json'})
        return response.json()

    def get_properties_from_json(self, exp_json):
        self.control_accs = [control["accession"] for control in exp_json["possible_controls"]]
        assert len(self.control_accs) == 1
        self.ctrl_acc = self.control_accs[0]
        self.ctrl_json = self.get_json(self.ctrl_acc)
        self.ctrl_num_reps = len(self.ctrl_json["replicates"])
        self.ctrl_fastq_files_json = [file for file in self.ctrl_json["files"] if file["file_format"] == "fastq"]

        self.cell_line = exp_json["biosample_summary"]
        self.target = exp_json["target"]["label"]
        self.eclip_num_reps = len(exp_json["replicates"])
        self.eclip_fastq_files_json = [file for file in exp_json["files"] if file["file_format"] == "fastq"]
        self.num_files = len(self.eclip_fastq_files_json) + len(self.ctrl_fastq_files_json)
        self.total_download_size = reduce(lambda file_size, file:
                                          file_size + int(file["cloud_metadata"]["file_size"]),
                                          self.eclip_fastq_files_json + self.ctrl_fastq_files_json, 0)

    def create_folder_heirarchy(self):
        self.paths = []
        for rep in range(1, self.eclip_num_reps + 1):
            path = "./fastqs/{cell_line}/{exp}_{target}/eclip/{exp}_{target}_rep{rep}".format(cell_line=self.cell_line,
                                                                                              exp=self.eclip_acc,
                                                                                              target=self.target,
                                                                                              rep=rep)
            self.paths.append(path)
        for rep in range(1, self.ctrl_num_reps + 1):
            path = "./fastqs/{cell_line}/{eclip_exp}_{target}/ctrl/{ctrl_exp}_{target}_rep{rep}".format(
                cell_line=self.cell_line,
                eclip_exp=self.eclip_acc, ctrl_exp=self.ctrl_acc, target=self.target, rep=rep)
            self.paths.append(path)
        for path in self.paths:
            os.makedirs(path, exist_ok=True)

    def create_table(self):
        def add_entries_for_exp(exp_type, file_json_list):
            for file in file_json_list:
                self.file = file
                rep = file["replicate"]["biological_replicate_number"]
                file_exp = file["replicate"]["experiment"]["accession"]
                file_acc = file["accession"]
                mate = file["paired_end"]
                url = file["cloud_metadata"]["url"]
                flowcell_details_len = len(file["flowcell_details"])
                if flowcell_details_len == 0:
                    barcode_id = ""
                    barcode_sequence = ""
                elif flowcell_details_len == 1:
                    barcode_id = file["flowcell_details"][0]["barcode"]
                    barcode_sequence = ""
                else:
                    barcode_id = file["flowcell_details"][0]["barcode"]
                    barcode_sequence = file["flowcell_details"][1]["barcode"]
                file_size = file["cloud_metadata"]["file_size"]
                filepath = ("./fastqs/{cell_line}/{eclip_exp}_{target}/{exp_type}/{exp}_{target}_rep{rep}/"
                            "{file_acc}_{target}_rep{rep}_mate{mate}.fastq.gz").format(cell_line=self.cell_line,
                                                                                       eclip_exp=self.eclip_acc,
                                                                                       exp=file_exp, target=self.target,
                                                                                       rep=rep,
                                                                                       file_acc=file_acc, mate=mate,
                                                                                       exp_type=exp_type)
                self.file_info_table["file_accession"].append(file_acc)
                self.file_info_table["file_path"].append(filepath)
                self.file_info_table["file_size"].append(file_size)
                self.file_info_table["replicate"].append(rep)
                self.file_info_table["mate"].append(mate)
                self.file_info_table["mate_accession"].append(file["paired_with"].strip("/").split("/")[-1])
                self.file_info_table["experiment_accession"].append(file_exp)
                self.file_info_table["target"].append(self.target)
                self.file_info_table["cell_line"].append(self.cell_line)
                self.file_info_table["eclip_experiment_accession"].append(self.eclip_acc)
                self.file_info_table["experiment_type"].append(exp_type)
                self.file_info_table["url"].append(url)
                self.file_info_table["barcode_id"].append(barcode_id)
                self.file_info_table["barcode_sequence"].append(barcode_sequence)

        add_entries_for_exp("eclip", self.eclip_fastq_files_json)
        add_entries_for_exp("ctrl", self.ctrl_fastq_files_json)

    def download_fastqs(self, queue=None):
        for filepath, url, file_acc in zip(self.file_info_table["file_path"],
                                           self.file_info_table["url"],
                                           self.file_info_table["file_accession"]):
            with open(filepath, 'wb') as out_file:
                out_file.write(requests.get(url).content)
            if queue is not None:
                queue.put(file_acc)


def initialize_downloaders(num_cores, eclip_accessions, working_directory):
    """
    Initializes instances of EncodeExperimentDownloader to gather information
    about the experiments from the ENCODE servers and calculate space necessary for download .
    :param num_cores: number of cores to use for initializing downloaders
    :type num_cores: int
    :param eclip_accessions: list of ENCODE accessions
    :type eclip_accessions: list
    :return: starmap_async result containing EncodeExperimentDownloader instances.
    """
    p = Pool(min(num_cores, 20))
    m = Manager()
    q = m.Queue()

    args = [(acc, q) for acc in eclip_accessions]
    result = p.starmap_async(EncodeExperimentDownloader, args)

    while not result.ready():
        print("Initializing accession downloaders... {}/{} finished".format(str(q.qsize()), len(eclip_accessions)),
              end="\r")
        time.sleep(1)

    initialized_downloaders = result.get()
    p.close()

    print("Done! {} downloaders initialized.".format(len(eclip_accessions)))
    total_size = reduce(lambda amt, size_obj: amt + size_obj.total_download_size, initialized_downloaders, 0)
    num_files = reduce(lambda amt, size_obj: amt + size_obj.num_files, initialized_downloaders, 0)
    print(num_files, "files, requiring", round(total_size / 1024 ** 3, 2), "GB")

    return initialized_downloaders


def begin_download(num_cores, ):
    def activate_download(downloader_instance, q):
        downloader_instance.download_fastqs(q)
        return downloader_instance

    p = Pool(min(num_cores, 12))
    m = Manager()
    q = m.Queue()

    args = [(downloader, q) for downloader in outputs]
    result = p.starmap_async(activate_download, args)

    while not result.ready():
        clear_output(wait=True)
        print("Running... {}/{} finished downloading".format(str(q.qsize()), num_files), end="\r")
        time.sleep(1)

    downloader_instances = result.get()
    p.close()
    print("Done! {} finished downloading.".format(q.qsize()))
    return downloader_instances


def build_file_table(downloader_instances):
    final_dict = {key: [] for key in downloader_instances[0].file_info_table.keys()}
    for instance in downloader_instances:
        for key in final_dict.keys():
            final_dict[key].extend(instance.file_info_table[key])

    file_table = pd.DataFrame(data=final_dict)
    file_table.set_index("file_accession", inplace=True)
    return file_table


def check_file_sizes(file_table):
    """
    Checks that downloaded files are of the expected size and returns a list of those that aren't.
    returned list is in the format [(file_accession, experiment_accession), ...]
    Could be useful if downloading got interrupted.
    :param file_table:
    :return:
    """
    redownload_list = []
    file_accs = []
    for idx, row in file_table.iterrows():
        path = row["file_path"]
        size = row["file_size"]
        disk_size = os.path.getsize(path)
        if disk_size != size:
            warn("File {path} does not have expected size".format())
            print(idx, size, disk_size)
            redownload_list.append(row["eclip_experiment_accession"])
            file_accs.append(idx)

    return zip(file_accs, redownload_list)  # (file_accession, experiment_accession)


def main(num_cores, eclip_accessions, working_directory):
    """
    Initializes file downloaders and starts multithreaded downloading of files from ENCODE.
    Returns a table with information on each accession/file and a list of downloaded files that don't
    match the expected file size.
    :param num_cores:
    :param eclip_accessions:
    :return:
    """
    # initialize/download files
    os.chdir(working_directory)
    downloader_instances = initialize_downloaders(num_cores, eclip_accessions, working_directory)
    if utils.yn_input("Do you want to start downloading?"):
        downloader_instances = begin_download(downloader_instances)
    else:
        print("Quitting pipeline.")
        exit()
    file_table = build_file_table(downloader_instances)
    bad_file_size_accs = check_file_sizes(file_table)

    return file_table, bad_file_size_accs
