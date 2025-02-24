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
        db = mysql.connector.connect(host=host, port=port, user=user, passwd=password, db=database)
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

@click.command()
@click.option("--input_file", "-i", type=click.Path(exists=True), help="Input file only containing sample name")
@click.option("--output", "-o", type=click.Path(), help="Output CSV file to save results.")
@click.option("--config_file", "-c", type=click.Path(), help="Configuration file for DB")
def main(input_file, output, config_file):
    """Reads sample names from a file and queries the database for sample and population IDs."""


    click.echo("🔍 Connecting to database....")
    config = configparser.ConfigParser()
    config.read(config_file)
    host = config['database']['host']
    port = config['database']['port']
    user = config['database']['user']
    database = config['database']['name']
    password = config['database']['password']

    results = []
    
    with open(input_file, "r") as f:
        sample_names = [line.strip() for line in f if line.strip()]

    click.echo("🔍 Querying database...")

    for sample_name in sample_names:
        sample_id, pop_id = get_sample_info(sample_name, host, port, database, user, password)
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
