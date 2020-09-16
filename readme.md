#eCLIP rRNA analysis pipeline
##Purpose
The purpose of this pipeline is to process publicly accessible 
eCLIP experiment data from the ENCODE project and analyze reads aligning to 
human rRNA. This pipeline will download, trim, align, filter, and summarize
data for use in statistical analysis of ribosome binding sites. To speed the 
analysis of large datasets, this pipeline makes use of multiple CPUs where 
possible.  

##Hardware requirements


##Software requirements
- Python 3.6
- [samtools](http://www.htslib.org/) 1.9
- [HISAT2](http://daehwankimlab.github.io/hisat2/) 2.1.0
- gzip 1.6
- [BBDuk](https://jgi.doe.gov/data-and-tools/bbtools/bb-tools-user-guide/bbduk-guide/) from 
[BBMap](https://jgi.doe.gov/data-and-tools/bbtools/) 38.44
- 

###Required Python modules
- Pandas 1.1.2
- Numpy 1.19.2
- Pysam 0.14.1
- Matplotlib 2.1.1

## Usage


## Data used here
From article : [Principles of RNA processing from analysis of enhanced CLIP maps for 150 RNA binding proteins](https://doi.org/10.1186/s13059-020-01982-9)  
Encode dataset accession: [ENCSR456FVU](https://www.encodeproject.org/publication-data/ENCSR456FVU/).   
Individual experiment accessions from [Table S1](https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-020-01982-9/MediaObjects/13059_2020_1982_MOESM1_ESM.xlsx)
of that publication. Data was reformatted into the provided file `encode_eclip_accessions.txt`  
Reference for downloading ENCODE data:
[Encode REST API with Python](https://www.encodeproject.org/help/rest-api/#json-script)


Human reference rRNA sequences downloaded from refseq Gene and combined into `hsrRNA.fa`.
- 5s: https://www.ncbi.nlm.nih.gov/gene/100169758  
- 18s: https://www.ncbi.nlm.nih.gov/gene/100008588  
- 5.8s: https://www.ncbi.nlm.nih.gov/gene/100008587  
- 28s: https://www.ncbi.nlm.nih.gov/gene/100008589 

A hisat2 index is provided in the directory `hisat2_index_hsrRNA`. It was 
generated with the following command:
```bash
hisat2-build ./hsrRNA.fa ./hisat2_index_hsrRNA/
```
An IGV genome file (`hsrRNAs.genome`) is provided for visualizing sequencing data.