import re

@click.command()
@click.option('--target_db', default='curated')
@click.option('--target_table', default='client_communication_preferences_journal')
@click.option('--as_of', required=True)
def main(target_db, target_table, as_of):
    # Validate the as_of parameter to ensure it matches the expected format (YYYYMMDD)
    if not re.match(r'^\d{8}$', as_of):
        raise ValueError("Invalid as_of format. Expected YYYYMMDD.")

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
        ...
    """

    df = sc.sql(qry).withColumn('start_date', f.col('start_date').cast('timestamp'))

    sc.save(
        df=df,
        database=target_db,
        table=target_table,
        journal_write=True,
        journal_write_as_of=as_of,
    )
