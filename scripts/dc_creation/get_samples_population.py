import click
import mysql.connector
import csv
import configparser
from mysql.connector import Error, InterfaceError, DatabaseError


def get_sample_info(sample_name, host, port, database, user, password):
    """Query the database to fetch sample ID and population ID for a given sample name."""
    query = """
        SELECT s.sample_id, spa.population_id
        FROM sample s
        JOIN dc_sample_pop_assign spa ON s.sample_id = spa.sample_id
        WHERE s.name = %s
    """

    try:
        db = mysql.connector.connect(
            host=host, port=port, user=user, passwd=password, db=database
        )
        cursor = db.cursor()
        cursor.execute(query, (sample_name,))
        results = cursor.fetchall()
        result = results[0] if results else (None, None)
        cursor.close()
        db.close()
        return result

    except InterfaceError as e:
        click.echo(f"❌ Connection issue: {e}")
    except DatabaseError as e:
        click.echo(f"❌ Database operation error: {e}")
    except Error as e:
        click.echo(f"❌ General MySQL error: {e}")

def check_sample_info_and_add(sample_name, host, port, database, user, password, samples_file):
    """Query the database to check that every sample in the input file exists in the database"""

    query = """ SELECT sample_id  from sample where name = %s """
    

    insert_into_query = """INSERT into sample(name, sex, sample_source_id) VALUES (%s, %s, %s)"""
    samples_file_list = []
    #get the list of samples in samples_file
    with open(samples_file, "r") as f:
        lines = f.readlines()

    samples_file_list = []  # Initialize before the loop

    try: 
        db = mysql.connector.connect(host=host, port=port, user=user, password=password, db=database)
        cursor = db.cursor()

        for line in lines: 
            columns = line.strip().split(";")
            if not columns or len(columns) < 3: 
                click.echo(f"❌ Skipping line: {columns} (Not enough columns)")
                continue

            samples_file_list.append(columns) 

            cursor.execute(query, (columns[0], ))
            sample_results = cursor.fetchone()

            if sample_results:
                continue

            click.echo(f"✅ Inserting: {columns}")  # Debugging
            cursor.execute(insert_into_query, (columns[0], columns[2], 1,))
            db.commit()

    except mysql.connector.Error as e:
        click.echo(f"❌ MySQL Error: {e}")

    finally:
        if db.is_connected():
            cursor.close()
            db.close()
        
    return samples_file_list

def fetch_sample_pop_info_differently(sample_name,host, port, database, user, password, samples_file_list):
    "Fetch the sample information differently  because this were none existing sample"
    #sample_pop_list = [] #list of lists

    sample_query = """ SELECT sample_id from sample where name = %s"""
    pop_query = """SELECT population_id from population where name = %s or description = %s"""

    try: 
        db = mysql.connector.connect(host=host, port=port, user=user, password=password, db=database)
        cursor = db.cursor()
        if any(sample_name in sublist for sublist in samples_file_list):
            cursor.execute(sample_query, (sample_name,))
            sample_results = cursor.fetchone()
            matching_list = next((sublist for sublist in samples_file_list if sample_name in sublist), None)
            if matching_list:
                cursor.execute(pop_query, (matching_list[1], matching_list[1]))
                pop_results = cursor.fetchone()
                result_list = [sample_name, sample_results[0], pop_results[0]]
                return result_list
        else:
            click.echo(f"❌ {sample_name} not in list")
    except Error as e:
         click.echo(f"❌ General MySQL error: {e}")

    finally:
        if db.is_connected():
            cursor.close()
            db.close()



@click.command()
@click.option(
    "--input_file",
    "-i",
    type=click.Path(exists=True),
    help="Input file only containing sample name",
    required=True,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output CSV file to save results.",
    required=True,
)
@click.option(
    "--config_file",
    "-c",
    type=click.Path(exists=True),
    help="Configuration file for DB",
    required=True,
)
@click.option(
    "--sample_file", 
    "-s",
    type=click.Path(exists=True),
    help="File containing sample and population information"
)
def main(input_file, output, config_file, sample_file):
    """Reads sample names from a file and queries the database for sample and population IDs.
    Optional usage - 
    If new samples, it checks it does not exists in the database and adds it then fetches the information from the sample and population table, all you need is a samples file in the format
    sample_name,population,sex"""

    click.echo("🔍 Connecting to database....")
    config = configparser.ConfigParser()
    config.read(config_file)
    host = config["database"]["host"]
    port = config["database"]["port"]
    user = config["database"]["user"]
    database = config["database"]["name"]
    password = config["database"]["password"]

    results = []

    with open(input_file, "r") as f:
        sample_names = [line.strip() for line in f if line.strip()]

    click.echo("🔍 Querying database...")

    for sample_name in sample_names:
        sample_id, pop_id = get_sample_info(
            sample_name, host, port, database, user, password
        )
        if not sample_id and sample_file:
            click.echo("🔍 Checking sample info and adding......")
            sample_list = check_sample_info_and_add(sample_name, host, port, database, user, password, sample_file)
            click.echo(f"🔍 Fetching sample and population differently because {sample_name} was not in DB")
            diff_result = fetch_sample_pop_info_differently(sample_name,host, port, database, user, password, sample_list)
            results.append((diff_result))
            continue
        results.append((sample_name, sample_id, pop_id))

    click.echo(f"✅ Sample and population fetched")
    # Save results to a CSV file if specified
    if output:
        with open(output, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Sample Name", "Sample ID", "Population ID"])
            writer.writerows(results)
        click.echo(f"📁 Results saved to {output}")


if __name__ == "__main__":
    main()
