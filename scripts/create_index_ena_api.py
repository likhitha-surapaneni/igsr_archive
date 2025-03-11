import csv
import requests
import click
import sys

# # Input and output file names
# input_csv = "supplementary.csv"
# output_tsv = "output.tsv"

@click.command()
@click.option("--input_file", "-i", type=click.Path(exists=True), help="Input file containing file accession column and project accession")
@click.option("--output_file", "-o", help="Output index file accession column")


def get_data_from_ena(input_file, output_file):
    url = "https://www.ebi.ac.uk/ena/portal/api/search"
    # Read CSV and process each row
    with open(input_file, newline='', encoding='utf-8') as csvfile, open(output_file, 'w', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(csvfile, delimiter=',') 
        writer = None
        tsvfile.write("##Date=20250305\n")
        tsvfile.write("##HGSVC PHASE 3\n")
        tsvfile.write("##RUN_ACCESSION=ENA/SRA assigned accession for the run\n")
        tsvfile.write("##SRA_MD5=MD5 for the file according to SRA\n")
        tsvfile.write("##SUBMITTED_MD5 = MD5 for the file on submission\n")
        tsvfile.write("##FASTQ_FTP=ENA/SRA FTP fath from which the FASTQ file can be downloaded\n")
        tsvfile.write("##SAMPLE_ACCESSION=ENA/SRA assigned accession for the sample\n")
        tsvfile.write("##STUDY_ACCESSION=ENA/SRA assigned accession for the study\n")
        tsvfile.write("##CENTER_NAME=sequencing center that produced and submitted the sequence data\n")
        tsvfile.write("##SUBMISSION_ACCESSION=ENA/SRA assigned accession for this submission\n")
        tsvfile.write("##SUBMITTED_FTP=Submission FTP for this submission\n")
        tsvfile.write("##SAMPLE_TITLE=Title for the submitted sample\n")
        tsvfile.write("##SAMPLE_DESCRIPTION=Description of the sample, usually Technology\n")
        tsvfile.write("##Country=Country of the sample\n")
        tsvfile.write("##EXPERIMENT_ACCESSION=ENA/SRA assigned accession for the experiment\n")
        tsvfile.write("##INSTRUMENT_PLATFORM=type of sequencing machine used in the experiment\n")
        tsvfile.write("##INSTRUMENT_MODEL=model of the sequencing machine used in the experiment\n")
        tsvfile.write("##LIBRARY_NAME=identifier for the library\n")
        tsvfile.write("##RUN_ALIAS=run name assigned by the sequencing machine\n")
        tsvfile.write("##RUN_DATE=date the run was done\n")
        tsvfile.write("##LIBRARY_MAX_FRAGMENT_SIZE=submitter specified insert size of the library\n")
        tsvfile.write("#LIBRARY_LAYOUT=Library layout, this can be either PAIRED or SINGLE\n")
        tsvfile.write("##FASTQ_ASPERA=ASPERA Path for which FASTQ file can be downloaded\n")
        tsvfile.write("##READ_COUNT=number of reads in the run, two mates are considered as one read\n")


        for i,row in enumerate(reader):
            file_accession = row["file accession"]
            project_accession = row["project accession"]

            if file_accession is None:
                click.echo(f"Your file does not contain file accession information")
                sys.exit()

            if project_accession is None: 
                click.echo(f"Your file does not contain project accession information")
                sys.exit()

            query = f'result=read_run&query=run_accession%3D%22{file_accession}%22%20AND%20study_accession%3D%22{project_accession}%22&fields=fastq_ftp%2Csra_md5%2Csubmitted_md5%2Crun_accession%2Csample_accession%2Cstudy_accession%2Ccenter_name%2Csubmission_accession%2Csubmitted_ftp%2Csample_title%2Csample_description%2Ccountry%2Cexperiment_accession%2Cinstrument_platform%2Cinstrument_model%2Clibrary_name%2Crun_alias%2Crun_date%2Clibrary_max_fragment_size%2Clibrary_layout%2Cfastq_aspera%2Cread_count&format=tsv'


            
            # Make the API request
            response = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=query)
            
            if response.status_code == 200:
                lines = response.text.strip().split("\n")
                if len(lines) > 1:
                    if i == 0: # to write header for only the first role
                        tsvfile.write(f"#{lines[0].upper()}" + "\n")
                    for line in lines[1:]:
                        tsvfile.write(line + "\n")
                else:
                    click.echo(f"No results for {file_accession}")
            else:
                click.echo(f"Failed request for {file_accession}: {response.status_code}")

if __name__ == "__main__":
    get_data_from_ena()