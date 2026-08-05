# --- Connection settings ---
# Using SQL Server Authentication (username/password) — confirmed via
# check_auth_type.py, so USERNAME and PASSWORD must be filled in below.
SERVER = "uszwphqtapdb001.database.windows.net"
DATABASE = "uszwphqtapdb001"
USERNAME = "your_username"        # fill in your real SQL Server login
PASSWORD = "your_password"        # fill in your real SQL Server password

# --- Stage tables ---

STAGES = [
    {
        "key": "bronze_raw",
        "label": "Bronze Raw",
        "sublabel": "Raw ingested records",
        "description": "Description of what happens in this step.",
        "table": "dbo.Bronze_PII_Table_Raw",
    },
    {
        "key": "bronze_consolidated",
        "label": "Bronze Consolidated",
        "sublabel": "After deduplication",
        "description": "Description of what happens in this step.",
        "table": "dbo.Bronze_PII_Table_Consolidated",
        # Which stage's total this stage reconciles FROM — used to show
        # "Starting Total - exclusions = Ending Total" math, same pattern
        # as the Mosaic dashboard's reconciliation boxes.
        "reconcile_from_key": "bronze_raw",
        # Confirmed against real schema (as of July 31, 2026):
        # - BRONZE_ROW_HASH exists on BOTH Raw and Consolidated tables
        # - SILVER_PROCESSING_STATUS only exists on Consolidated, and showed
        #   NULL across the sample checked — treated as "not yet processed"
        #   for now. Worth re-confirming with the full GROUP BY once more
        #   data / real Silver processing exists.
        "breakdown": [
            {
                "name": "Exact Duplicate Records Removed",
                "query": (
                    "SELECT COUNT(*) - COUNT(DISTINCT BRONZE_ROW_HASH) "
                    "FROM dbo.Bronze_PII_Table_Raw"
                ),
            },
            {
                # Requested by Melissa via Teams: "add in a number of records
                # that are moved to the errors table in the bronze
                # consolidated section... to see how the population is
                # narrowed down."
                # Corrected 8/5 to match the real stored procedure found in
                # dbo.Get_Bronze_Reconciliation_Dashboard: uses
                # COUNT(DISTINCT BRONZE_ROW_HASH), not COUNT(*), on the
                # Errors table — this is what makes the reconciliation
                # balance exactly (13,601,232 − 2,224,493 − 207,507 =
                # 11,169,232), confirmed against real numbers on 8/5.
                "name": "Unique Records Failing Validation (Errors)",
                "query": "SELECT COUNT(DISTINCT BRONZE_ROW_HASH) FROM dbo.Bronze_PII_Errors",
            },
        ],
        # NOTE: "Records Queued for Processing" (SILVER_PROCESSING_STATUS
        # IS NULL) was removed from here on 8/5 — it was found to measure
        # almost the entire Consolidated table's current status, not a
        # real exclusion between Raw and Consolidated, so it broke the
        # reconciliation math (its count matched the final total almost
        # exactly). It's a genuinely useful number, just not a subtraction
        # item — worth showing separately (e.g. its own stat) if wanted,
        # not inside this ledger.
    },
    {
        "key": "silver_stage1",
        "label": "Silver — Stage 1",
        "sublabel": "Initial enrichment",
        "description": "Description of what happens in this step.",
        "table": "silver.stg_dataload_person_silver",
    },
    {
        "key": "silver_cleaned",
        "label": "Silver — Cleaned",
        "sublabel": "Quality validated",
        "description": "Description of what happens in this step.",
        "table": "silver.stg_dataload_person_cleaned",
    },
    {
        "key": "gold_entities",
        "label": "Gold Entities",
        "sublabel": "Resolved identities",
        "description": "Description of what happens in this step.",
        "table": "gold.stg_dataload_person_gold",
    },
]

# Output file — this is the dashboard you open in your browser.
# Named v2 to keep it separate from your working v1 dashboard, in case you
# want to compare them side by side or roll back.
OUTPUT_HTML = r"G:\srini\dashboard_live_funnel_v2.html"
