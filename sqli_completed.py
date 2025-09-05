import re
import click
from pyspark.sql import SparkSession, functions as f

@click.command()
@click.option('--target_db', default='curated')
@click.option('--target_table', default='client_communication_preferences_journal')
@click.option('--as_of', required=True)
def main(target_db, target_table, as_of):
    # Validate as_of parameter 
    if not re.match(r'^\d{8}$', as_of):
        raise ValueError("Invalid as_of format. Expected YYYYMMDD.")

    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("DBWriteApp") \
        .enableHiveSupport() \       # enable if you are writing to Hive or Spark SQL catalog
        .getOrCreate()

    qry = f"""
        WITH blueshift_active_email_client_agg AS (
            SELECT client_id, 
                   MAX(last_opened_at) AS last_opened_at,
                   MIN(first_opened_at) AS first_opened_at
            FROM blueshift.campaign_activity_kpis
            WHERE DATE(last_opened_at) <= TO_DATE('{as_of}', 'yyyyMMdd')
               OR last_opened_at IS NULL
               OR DATE(first_opened_at) <= TO_DATE('{as_of}', 'yyyyMMdd')
            GROUP BY 1
        )
        -- more CTEs / query goes here
        SELECT * FROM blueshift_active_email_client_agg
    """

    # Run the query
    df = spark.sql(qry).withColumn('start_date', f.col('first_opened_at').cast('timestamp'))

    # Prepare full table name
    full_table_name = f"{target_db}.{target_table}"

    # Save DataFrame to specified table (overwrite, append, etc. as appropriate)
    df.write.mode('append').saveAsTable(full_table_name)

    spark.stop()

if __name__ == "__main__":
    main()
