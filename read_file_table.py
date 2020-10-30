import numpy as np
import pandas as pd


def get_ctrl_file_table(path, make_csv=False):
    '''
    Reads input file_table.csv file and outputs .csv table listing Experiment_accessions for the controls of each target
    Accepts "make_csv" boolean argument if user wants to output table
    '''
    file_table = pd.read_csv(path)
    # print(file_table.columns)
    ctrls = file_table[(file_table['experiment_type'] == "ctrl") & (file_table['mate'] == 1)]
    hepg2_ctrls = file_table[
        (file_table['experiment_type'] == "ctrl") & (file_table['mate'] == 1) & (file_table['cell_line'] == "HepG2")]
    k562_ctrls = file_table[
        (file_table['experiment_type'] == "ctrl") & (file_table['mate'] == 1) & (file_table['cell_line'] == "K562")]

    assert len(ctrls) == (len(hepg2_ctrls) + len(k562_ctrls)), "Uncaptured cell line control rows!"

    ctrls = ctrls.loc[:, ['target', 'cell_line', 'experiment_type', 'experiment_accession']]
    hepg2_ctrls = hepg2_ctrls.loc[:, ['target', 'cell_line', 'experiment_type', 'experiment_accession']]
    k562_ctrls = k562_ctrls.loc[:, ['target', 'cell_line', 'experiment_type', 'experiment_accession']]

    if make_csv:
        ctrl_output_path = path.replace(".csv", "_ctrls.csv")
        hepg2_ctrls_output_path = path.replace(".csv", "_ctrls_hepg2.csv")
        k562_ctrls_output_path = path.replace(".csv", "_ctrls_K562.csv")

        ctrls.to_csv(ctrl_output_path)
        hepg2_ctrls.to_csv(hepg2_ctrls_output_path)
        k562_ctrls.to_csv(k562_ctrls_output_path)
    return ctrls


def get_multiindex_ctrl_file_table(path, make_csv=False):
    '''
    Reads input file_table.csv file and outputs .csv table listing experiment_accessions for the controls of each target.
    Output .csv file is multiindexed by target + cell_line.
    Accepts "make_csv" boolean argument if user wants to output table
    '''
    file_table = pd.read_csv(path)
    target_table = file_table[(file_table['mate'] == 1) & (file_table['replicate'] == 1)]
    target_table = target_table.set_index(['target', 'cell_line'])
    target_table = target_table.loc[:, ['experiment_type', 'experiment_accession']]

    if make_csv:
        output_path = path.replace(".csv", "_ctrls_multiindex.csv")
        target_table.to_csv(output_path)
    return target_table


if __name__ == "__main__":
    path = "/Users/lij/PycharmProjects/eclip_analysis_pipeline/file_table.csv"
    get_ctrl_file_table(path, make_csv=True)
    get_multiindex_ctrl_file_table(path, make_csv=True)