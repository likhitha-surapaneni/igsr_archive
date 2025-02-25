import click
import sys
import mysql.connector
import configparser
from mysql.connector import Error


def insert_info_into_dc_pop_assign(
    did, sid, popid, host, port, user, database, password
):
    try:
        # insert_query into dc sample pop assign
        insert_query = """ INSERT into dc_sample_pop_assign (sample_id, population_id, data_collection_id) 
        VALUES (%s, %s, %s )
"""
        db = mysql.connector.connect(
            host=host, port=port, user=user, database=database, password=password
        )
        cursor = db.cursor()
        cursor.execute(
            insert_query,
            (
                sid,
                popid,
                did,
            ),
        )
        db.commit()

    except Error as e:
        click.echo(f"❌ Connection issue: {e}")
        sys.exit()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def get_data_collection_id(code, host, port, user, database, password):
    try:
        # select query from data collection
        select_query = """
        SELECT data_collection_id from data_collection where code = %s
        """

        db = mysql.connector.connect(
            host=host, port=port, user=user, database=database, password=password
        )
        cursor = db.cursor()
        cursor.execute(select_query, (code,))
        results = cursor.fetchone()
        result = (
            results[0]
            if results
            else click.echo("❌ There is no data collection with that code")
        )
        cursor.close()
        db.close()
        return result
    except Error as e:
        click.echo(f"❌ Connection issue: {e}")
        sys.exit()
    except InterfaceError as e:
        click.echo(f"❌ Interface Error issue: {e}")
        sys.exit()
    except DatabaseError as e:
        click.echo(f"❌ Database error issue: {e}")
        sys.exit()


@click.command()
@click.option(
    "--input_file",
    "-i",
    type=click.Path(exists=True),
    help="Input file only sample id and population id",
    required=True,
)
@click.option(
    "--config_file",
    "-c",
    type=click.Path(exists=True),
    help="Config file for database setup",
)
@click.option("--code", "-code", type=str, help="Data collection code")
def main(input_file, config_file, code):
    """
    Uses the data collection and the input file to populate the dc_sample_pop assign table
    """
    click.echo("🔍 Connecting to database....")
    config = configparser.ConfigParser()
    config.read(config_file)
    host = config["database"]["host"]
    port = config["database"]["port"]
    user = config["database"]["user"]
    database = config["database"]["name"]
    password = config["database"]["password"]

    click.echo("🔍 Fetching data collection inforamtion....")
    no_sample = []

    did = get_data_collection_id(code, host, port, user, database, password)

    if did:
        click.echo(f"✅ Data collection id is {did}")
        with open(input_file, "r") as file:
            lines = file.readlines()[1:]
        for line in lines:
            columns = line.strip().split(",")
            sid, popid = columns[1], columns[2]
            if not sid:
                no_sample.append(columns[0])
                continue
            click.echo("🔍 Inserting into dc_pop_assign....")
            insert_info_into_dc_pop_assign(
                did, sid, popid, host, port, user, database, password
            )
    string_no_samples = (",").join(no_sample)
    click.echo(
        f"Samples that do not have a sample id in the database are {string_no_samples}."
    )
    click.echo(f"✅ All values in file {input_file} have been inserted into db")


if __name__ == "__main__":
    main()
