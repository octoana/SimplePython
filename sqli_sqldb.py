import re
import click
import pandas as pd
from sqlalchemy import create_engine, text

@click.command()
@click.option('--target_db', default='curated')
@click.option('--target_table', default='client_communication_preferences_journal')
@click.option('--as_of', required=True)
def main(target_db, target_table, as_of):
    # Validate the as_of parameter to ensure it matches the expected format (YYYYMMDD)
    if not re.match(r'^\d{8}$', as_of):
        raise ValueError("Invalid as_of format. Expected YYYYMMDD.")

    # MySQL connection setup (update with your credentials)
    user = 'your_username'
    password = 'your_password'
    host = 'your_mysql_host'
    port = 3306
    # For source queries, set the right database!
    source_db = 'blueshift'
    url = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{source_db}'
    engine = create_engine(url)

    # Convert 'as_of' to DATE in python, or use as string for SQL
    as_of_date = as_of  # e.g. '20230101'

    # Rewrite your SQL query as needed!
    qry = f"""
        WITH blueshift_active_email_client_agg AS (
            SELECT client_id, 
                   MAX(last_opened_at) AS last_opened_at,
                   MIN(first_opened_at) AS first_opened_at
            FROM campaign_activity_kpis
            WHERE (DATE(last_opened_at) <= STR_TO_DATE('{as_of_date}', '%Y%m%d')
               OR last_opened_at IS NULL
               OR DATE(first_opened_at) <= STR_TO_DATE('{as_of_date}', '%Y%m%d'))
            GROUP BY client_id
        )
        -- continue your SQL...
    """

    # Run the query (using pandas to pull result as dataframe)
    df = pd.read_sql_query(qry, engine)

    # Cast your date columns in pandas as needed, e.g.
    # df['start_date'] = pd.to_datetime(df['start_date'])

    # Write the DataFrame to the target MySQL table (append or replace as needed)
    # "journal_write" logic needs to be implemented in custom code (archive, update, etc.)
    target_url = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{target_db}'
    target_engine = create_engine(target_url)

    # Example: simple append; for more complex "journal_write", you'd need to implement logic manually
    df.to_sql(target_table, target_engine, if_exists='append', index=False)

if __name__ == '__main__':
    main()
