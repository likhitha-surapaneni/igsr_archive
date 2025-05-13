import csv
import requests
import click
import sys
import os
# # Input and output file names
# input_csv = "supplementary.csv"
# output_tsv = "output.tsv"

url = "https://www.ebi.ac.uk/ena/portal/api/search"

@click.command()
@click.option("--input_file", "-i", type=click.Path(exists=True), help="Input file containing file accession column and project accession")
@click.option("--output_file", "-o", help="Output index file accession column", required=True)
@click.option("--date", "-d", help="Date of the run in the format YYYYMMDD eg 20250305", required=True)
@click.option("--project", "-p", help="Project accession")

def get_data_from_ena(input_file: str, output_file: str, date: str, project: str) -> None:
    """
        Function that fetches data from the ENA API using the run accession and study accession 

        Args:
            input_file (str): Input file containing the run accession and study accession, we expect the column to be file accession and study accesssion
            output_file (str): Output file containing all the data fetched from the ENA API
            date (str): Date in the format YYYYMMDDD
            project(str): Project accession in the case of no input_file
    """    
    
    # Read CSV and process each row
    if input_file and project:
        click.echo("❌Can not run both --project and --input_file at the same time")
        sys.exit()
    if input_file:
         input_file_process(input_file, output_file, date)
    if project:
         accession_process(project, output_file, date)
    else: 
         click.echo(f"--project or --input file needs to be defined")
         sys.exit()


def input_file_process(input_file: str, output_file: str, date: str) :
    """If input file is called on the command line, this is the function that runs

    Args:
        input_file (str): Input file containing the run accession and study accession, we expect the column to be file accession and study accesssion
        output_file (str): Output file containing all the data fetched from the ENA API
        date (str): Date in the format YYYYMMDDD
    """        
        
    with open(input_file, newline='', encoding='utf-8') as csvfile, open(output_file, 'w', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(csvfile, delimiter=',') 
        writer = None
        tsvfile.write(f"##Date={date}\n")
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
        tsvfile.write("##LIBRARY_LAYOUT=Library layout, this can be either PAIRED or SINGLE\n")
        tsvfile.write("##FASTQ_ASPERA=ASPERA Path for which FASTQ file can be downloaded\n")
        tsvfile.write("##READ_COUNT=number of reads in the run, two mates are considered as one read\n")

        
        for i,row in enumerate(reader):
            file_accession = row["file accession"]
            project_accession = row["project accession"]


            check_file_accession(file_accession)
    
            check_project_accession(project_accession)

            query = construct_query(file_accession, project_accession)
            
            # Make the API request
            lines = return_response(query, file_accession)
            if len(lines) > 1:
                if i == 0: # to write header for only the first role
                    tsvfile.write(f"#{lines[0].upper()}" + "\n")
                for line in lines[1:]:
                    tsvfile.write(line + "\n")
                click.echo(f"✅Results have been written to the {output_file}")
            else:
                click.echo(f"❌No results for {file_accession}")

def accession_process(project: str, output_file: str, date: str):
    """If project accession is called, this is the function that runs

    Args:
        project (str): Project accession
        output_file (str): Output file containing all the data fetched from the ENA API
        date (str): Date in the format YYYYMMDDD
    """    
    with open(output_file, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = None
        tsvfile.write(f"##Date={date}\n")
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
        tsvfile.write("##LIBRARY_LAYOUT=Library layout, this can be either PAIRED or SINGLE\n")
        tsvfile.write("##FASTQ_ASPERA=ASPERA Path for which FASTQ file can be downloaded\n")
        tsvfile.write("##READ_COUNT=number of reads in the run, two mates are considered as one read\n")

        file_accession = None
        query = construct_query(file_accession, project)

        lines = return_response(query, project)
        if len(lines) > 1:
            for line in lines[1:]:
                tsvfile.write(line + "\n")
            click.echo(f"✅Results have been written to the {output_file}")
        else:
            click.echo(f"❌No results for {project}")


def check_file_accession(accession: str) -> None:
    """
        Checks the file contains the column file accession 
        #To do - Maybe check for also Run accession 

        Args:
            accession (str): Accession
    """    
    if accession is None:
         click.echo(f"❌Your file does not contain file accession information")
         sys.exit()

def check_project_accession(accession: str) -> None:
    """
        Checks the file contains the column project accession

        Args:
            accession (str): Column accession
    """    
    if accession is None:
        click.echo(f"❌Your file does not contain project accession information")
        sys.exit()

def construct_query(file_accession: str, project_accession: str) -> str:
    """
        Constructs the API query string

        Args:
            file_accession (str): Run accession - file accession column
            project_accession (str): Study accession - project accession column

        Returns:
            str: Query formed.
    """    
    if file_accession:
        base_query = (
            f'result=read_run&query=run_accession%3D%22{file_accession}%22%20AND%20'
            f'study_accession%3D%22{project_accession}%22&fields='
            'fastq_ftp%2Csra_md5%2Csubmitted_md5%2Crun_accession%2Csample_accession%2C'
            'study_accession%2Ccenter_name%2Csubmission_accession%2Csubmitted_ftp%2C'
            'sample_title%2Csample_description%2Ccountry%2Cexperiment_accession%2C'
            'instrument_platform%2Cinstrument_model%2Clibrary_name%2Crun_alias%2C'
            'run_date%2Clibrary_max_fragment_size%2Clibrary_layout%2Cfastq_aspera%2C'
            'read_count&format=tsv'
        )

    base_query = (f'result=read_run&query=study_accession%3D%22{project_accession}%22&fields='
              'fastq_ftp%2Csra_md5%2Csubmitted_md5%2Crun_accession%2Csample_accession%2C'
              'study_accession%2Ccenter_name%2Csubmission_accession%2Csubmitted_ftp%2C'
              'sample_title%2Csample_description%2Ccountry%2Cexperiment_accession%2C'
              'instrument_platform%2Cinstrument_model%2Clibrary_name%2Crun_alias%2C'
              'run_date%2Clibrary_max_fragment_size%2Clibrary_layout%2Cfastq_aspera%2C'
              'read_count&format=tsv')

    return base_query

def return_response(query: str, accesion: str) -> str:
    """
        Process the response from the ENA API

        Args:
            query (str): Query
            file_accesion (str): Run accesssion 

        Returns:
            str:    The response text
    """    
    if query:
        response = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=query)
        if response.status_code == 200:
                lines = response.text.strip().split("\n")
                return lines
        else:
            click.echo(f"❌Failed request for {accesion}: {response.status_code}")



if __name__ == "__main__":
    get_data_from_ena()