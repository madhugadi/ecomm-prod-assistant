# --- Connection settings ---
# Using SQL Server Authentication (username/password) — confirmed via
# check_auth_type.py, so USERNAME and PASSWORD must be filled in below.
SERVER = "your_server_name"       # e.g. "SQLSRV01" or "localhost\\SQLEXPRESS"
DATABASE = "your_database_name"   # e.g. "igloo_analytics"
USERNAME = "your_username"        # fill in your real SQL Server login
PASSWORD = "your_password"        # fill in your real SQL Server password

# --- Stage tables ---
# Same 5-stage structure as Project Mosaic. Update these to the real igloo
# table names (schema.table format if needed, e.g. "bronze.stg_dataload_person_raw").
STAGES = [
    {
        "key": "bronze_raw",
        "label": "Bronze Raw",
        "sublabel": "Raw ingested records",
        "table": "bronze.stg_dataload_person_raw",
    },
    {
        "key": "bronze_consolidated",
        "label": "Bronze Consolidated",
        "sublabel": "After deduplication",
        "table": "bronze.stg_dataload_person_consolidated",
    },
    {
        "key": "silver_stage1",
        "label": "Silver — Stage 1",
        "sublabel": "Initial enrichment",
        "table": "silver.stg_dataload_person_silver",
    },
    {
        "key": "silver_cleaned",
        "label": "Silver — Cleaned",
        "sublabel": "Quality validated",
        "table": "silver.stg_dataload_person_cleaned",
    },
    {
        "key": "gold_entities",
        "label": "Gold Entities",
        "sublabel": "Resolved identities",
        "table": "gold.stg_dataload_person_gold",
    },
]

# Output file — this is the dashboard you open in your browser.
OUTPUT_HTML = "dashboard_live_funnel.html"