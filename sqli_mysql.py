import re
import click
import pandas as pd
import pymysql

@click.command()
@click.option('--target_db', default='curated', help='Target MySQL database')
@click.option('--target_table', default='client_communication_preferences_journal', help='Target table')
@click.option('--as_of', required=True, help='Snapshot date in YYYYMMDD format')
def main(target_db, target_table, as_of):
    # Validate 'as_of' parameter: must be YYYYMMDD
    if not re.match(r'^\d{8}$', as_of):
        raise ValueError("Invalid as_of format. Expected YYYYMMDD.")

    # Dummy MySQL credentials (replace with your own as needed)
    user = 'myuser'
    password = 'mypassword'
    host = 'mysql1.mycorp.io'
    port = 3306

    source_db = 'blueshift'

    # Connect to source database
    source_conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=source_db,
        port=port,
        cursorclass=pymysql.cursors.DictCursor  # So pandas gets dicts not tuples
    )

    as_of_date = as_of

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
        -- YOUR REMAINING QUERY HERE
        SELECT * FROM blueshift_active_email_client_agg
    """

    # Get data as DataFrame
    df = pd.read_sql(qry, source_conn)

    # Optionally process DataFrame, e.g. convert date columns
    # df['start_date'] = pd.to_datetime(df['start_date'])

    # Connect to TARGET database for insert
    target_conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=target_db,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

    # Prepare INSERT statement
    if not df.empty:
        cols = list(df.columns)
        values = [tuple(row) for row in df.values]

        insert_stmt = f"INSERT INTO {target_table} ({', '.join(cols)}) VALUES ({', '.join(['%s']*len(cols))})"

        with target_conn.cursor() as cursor:
            cursor.executemany(insert_stmt, values)
        target_conn.commit()
        print(f"Inserted {len(df)} rows into {target_db}.{target_table}")
    else:
        print("No data to insert.")

    source_conn.close()
    target_conn.close()

if __name__ == '__main__':
    main()
