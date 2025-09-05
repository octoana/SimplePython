import re
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def main():
    # Read from JSON payload or form
    data = request.get_json() or request.form
    target_db = data.get('target_db', 'curated')
    target_table = data.get('target_table', 'client_communication_preferences_journal')
    as_of = data.get('as_of')
    
    # Validate the as_of parameter to ensure it matches the expected format (YYYYMMDD)
    if not as_of or not re.match(r'^\d{8}$', as_of):
        return jsonify({"error": "Invalid as_of format. Expected YYYYMMDD."}), 400

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
    return jsonify({"status": "OK"})

import os

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
