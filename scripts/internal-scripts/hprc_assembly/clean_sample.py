import csv

import os
import re


directory = '/homes/likhithas/IGSR/testing/igsr-code/scripts/elasticsearch/data/'

# for filename in os.listdir(directory):
# filepath = os.path.join(directory, "illumina_fastq.tsv")
# if os.path.isfile(filepath):
#     with open('/homes/likhithas/IGSR/testing/igsr-code/scripts/elasticsearch/data2/illumina_fastq.tsv','a', newline='', encoding='utf-8') as tsvfile:
#         with open(filepath, newline='') as file:  
#             reader = csv.reader(file, delimiter='\t')
#             for row in reader:
#                 fastq_ftp = row[3]
#                 sample_name = row[9].split("-")[0]
#                 line = f"{sample_name}\t{fastq_ftp}\n"
#                 tsvfile.write(line)


# filepath = os.path.join(directory, "oxford_fastq.tsv")
# if os.path.isfile(filepath):
#     with open('/homes/likhithas/IGSR/testing/igsr-code/scripts/elasticsearch/data2/oxford_fastq.tsv','a', newline='', encoding='utf-8') as tsvfile:
#         with open(filepath, newline='') as file:  
#             reader = csv.reader(file, delimiter='\t')
#             for row in reader:
#                 fastq_ftp = row[3]
#                 sample_name = row[9]
#                 if sample_name == "Human sample from Homo sapiens":
#                     continue
#                 line = f"{sample_name}\t{fastq_ftp}\n"
#                 tsvfile.write(line)


# filepath = os.path.join(directory, "pacbio_fastq.tsv")


# if os.path.isfile(filepath):
#     with open('/homes/likhithas/IGSR/testing/igsr-code/scripts/elasticsearch/data2/pacbio_fastq.tsv','a', newline='', encoding='utf-8') as tsvfile:
#         with open(filepath, newline='') as file:  
#             reader = csv.reader(file, delimiter='\t')
#             for row in reader:
#                 fastq_ftp = row[3]
#                 sample_name = row[9]
#                 match = re.search(r'[a-zA-Z]+[0-9]+[a-zA-Z]', sample_name)
#                 if sample_name == "Human sample from Homo sapiens":
#                     continue
#                 elif match:
#                     print(sample_name)
#                     sample_name = sample_name[:-1]
#                 line = f"{sample_name}\t{fastq_ftp}\n"
#                 tsvfile.write(line)


# filepath = os.path.join(directory, "pacbio_bam.tsv")


# if os.path.isfile(filepath):
#     with open('/homes/likhithas/IGSR/testing/igsr-code/scripts/elasticsearch/data2/pacbio_bam.tsv','a', newline='', encoding='utf-8') as tsvfile:
#         with open(filepath, newline='') as file:  
#             reader = csv.reader(file, delimiter='\t')
#             for row in reader:
#                 fastq_ftp = row[8]
#                 sample_name = row[9]
#                 match = re.search(r'[a-zA-Z]+[0-9]+[a-zA-Z]', sample_name)
#                 if sample_name == "Human sample from Homo sapiens":
#                     continue
#                 elif match:
#                     print(sample_name)
#                     sample_name = sample_name[:-1]
#                 line = f"{sample_name}\t{fastq_ftp}\n"
#                 tsvfile.write(line)

filepath = os.path.join(directory, "oxford_bam.tsv")


if os.path.isfile(filepath):
    with open('/homes/likhithas/IGSR/testing/igsr-code/scripts/elasticsearch/data2/oxford_bam.tsv','a', newline='', encoding='utf-8') as tsvfile:
        with open(filepath, newline='') as file:  
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                fastq_ftp = row[8]
                sample_name = row[9]
                match = re.search(r'[a-zA-Z]+[0-9]+[a-zA-Z]', sample_name)
                if sample_name == "Human sample from Homo sapiens":
                    continue
                elif match:
                    print(sample_name)
                    sample_name = sample_name[:-1]
                line = f"{sample_name}\t{fastq_ftp}\n"
                tsvfile.write(line)