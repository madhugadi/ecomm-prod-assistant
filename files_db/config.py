

STAGES = [
    {
        "key": "bronze_raw",
        "label": "Bronze Raw",
        "sublabel": "Raw ingested records",
        "description": "Raw records loaded directly from staging, organized by batch code. No processing has been applied yet.",
        "table": "dbo.Bronze_PII_Table_Raw",
    },
    {
        "key": "bronze_consolidated",
        "label": "Bronze Consolidated",
        "sublabel": "After deduplication",
        "description": "Records are deduplicated using a full-row hash and checked against 6 data-quality rules. Records that fail are routed to an errors table instead of Consolidated.",
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

        # Requested by Melissa (lower priority): "add the error types we
        # found and how many records of each." Exact query from the real
        # stored procedure (dbo.Get_Bronze_Reconciliation_Dashboard,
        # Result Set 2) — not yet verified independently, but sourced
        # directly from a screenshot of that real, working procedure.
        "error_type_breakdown_query": (
            "SELECT ERROR_TYPE, COUNT(*) AS RecordCount "
            "FROM dbo.Bronze_PII_Errors "
            "GROUP BY ERROR_TYPE "
            "ORDER BY RecordCount DESC"
        ),
    },
    {
        "key": "silver_stage1",
        "label": "Silver — Stage 1",
        "sublabel": "Initial enrichment",
        "description": "Rules not yet finalized — the team is currently defining data-quality checks and eligibility criteria for moving records from Bronze Consolidated into Silver.",
        "table": "silver.stg_dataload_person_silver",
    },
    {
        "key": "silver_cleaned",
        "label": "Silver — Cleaned",
        "sublabel": "Quality validated",
        "description": "Rules not yet finalized — depends on the Silver Stage 1 criteria being defined first.",
        "table": "silver.stg_dataload_person_cleaned",
    },
    {
        "key": "gold_entities",
        "label": "Gold Entities",
        "sublabel": "Resolved identities",
        "description": "Rules not yet finalized — Gold-layer entity resolution logic has not been defined yet.",
        "table": "gold.stg_dataload_person_gold",
    },
]

# Output file — this is the dashboard you open in your browser.
# Named v2 to keep it separate from your working v1 dashboard, in case you
# want to compare them side by side or roll back.
OUTPUT_HTML = r"G:\srini\dashboard_live_funnel_v2.html"
