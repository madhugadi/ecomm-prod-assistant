"""
Igloo Pipeline Dashboard — basic version

Run this script to pull current row counts from each stage table in SQL
Server and regenerate the dashboard HTML file. Open the HTML file in your
browser to see the latest numbers. Re-run any time you want it to update.

Requires: pip install pyodbc
"""

import datetime
import json
import pyodbc

import config


def get_connection():
    if config.USERNAME and config.PASSWORD:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.SERVER};"
            f"DATABASE={config.DATABASE};"
            f"UID={config.USERNAME};"
            f"PWD={config.PASSWORD};"
        )
    else:
        # Windows Authentication
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config.SERVER};"
            f"DATABASE={config.DATABASE};"
            f"Trusted_Connection=yes;"
        )
    return pyodbc.connect(conn_str)


def get_counts(conn):
    """Query row count for each configured stage table, plus any
    'breakdown' sub-queries defined for that stage (e.g. duplicate counts,
    exclusion reasons).

    If a table or breakdown query fails (doesn't exist yet, wrong column
    name, etc.), that piece is marked unavailable instead of crashing the
    whole run — so one bad query doesn't take down the rest of the dashboard.
    """
    counts = []
    cursor = conn.cursor()
    for stage in config.STAGES:
        # --- main stage count (unchanged from before) ---
        try:
            query = f"SELECT COUNT(*) FROM {stage['table']}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            stage_result = {**stage, "count": count, "available": True}
        except pyodbc.Error:
            conn.rollback()
            stage_result = {**stage, "count": None, "available": False}

        # --- NEW: breakdown sub-queries, if this stage defines any ---
        breakdown_results = []
        for item in stage.get("breakdown", []):
            try:
                cursor.execute(item["query"])
                b_count = cursor.fetchone()[0]
                breakdown_results.append({"name": item["name"], "count": b_count, "available": True})
            except pyodbc.Error:
                conn.rollback()
                breakdown_results.append({"name": item["name"], "count": None, "available": False})

        stage_result["breakdown_results"] = breakdown_results

        # --- NEW: grouped breakdown, e.g. "error type -> count" where the
        # number of rows returned isn't known ahead of time (a GROUP BY
        # query), unlike the fixed single-value breakdown items above. ---
        group_query = stage.get("error_type_breakdown_query")
        group_results = []
        if group_query:
            try:
                cursor.execute(group_query)
                rows = cursor.fetchall()
                group_results = [{"name": str(row[0]), "count": row[1], "available": True} for row in rows]
            except pyodbc.Error:
                conn.rollback()
                group_results = []  # query failed (table/column missing) — show nothing rather than guess
        stage_result["error_type_breakdown"] = group_results

        counts.append(stage_result)
    return counts


def render_html(stage_counts, generated_at):
    # Default selected stage on page load: the last *available* one
    last_available_idx = max(
        (i for i, s in enumerate(stage_counts) if s["available"]), default=0
    )
    default_key = stage_counts[last_available_idx]["key"]

    # --- Left sidebar: one clickable card per stage (same visual as before,
    # but now with onclick + a data-key so JS knows which stage to show) ---
    cards_html = ""
    for i, stage in enumerate(stage_counts):
        active_class = " active" if stage["key"] == default_key else ""
        if stage["available"]:
            count_html = f"{stage['count']:,}"
            sublabel_html = stage["sublabel"]
        else:
            active_class += " pending"
            count_html = "—"
            sublabel_html = "Not yet available"
        cards_html += f"""
        <div class="stage-card{active_class}" id="card-{stage['key']}" onclick="selectStage('{stage['key']}')">
            <div class="stage-label">{stage['label'].upper()}</div>
            <div class="stage-count">{count_html}</div>
            <div class="stage-sublabel">{sublabel_html}</div>
        </div>"""

    # --- Embed all stage data as JSON so the browser can render the detail
    # panel instantly on click, with no server round-trip needed ---
    stages_json = json.dumps(stage_counts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Igloo — Pipeline Health Overview</title>
<style>
    :root {{
        --ink: #1A1A1E;
        --paper: #FFFFFF;
        --panel: #F7F6F4;
        --line: #E8E7E4;
        --muted: #6B6E76;
        --red: #ED3024;
        --red-dark: #C41F16;
        --red-wash: #FDEEED;
        --amber: #FFC72C;
        --pending: #B9BBC0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: "Helvetica Neue", -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
        background: var(--paper);
        color: var(--ink);
    }}
    .hero {{
        background: linear-gradient(135deg, var(--red), var(--red-dark));
        padding: 36px 40px;
    }}
    .hero-inner {{
        max-width: 1180px;
        margin: 0 auto;
    }}
    .eyebrow {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.14em;
        color: rgba(255,255,255,0.85);
        text-transform: uppercase;
        margin-bottom: 10px;
    }}
    .title {{
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: #FFFFFF;
    }}
    .subtitle {{
        font-size: 15px;
        font-weight: 500;
        color: rgba(255,255,255,0.85);
        margin-top: 6px;
    }}
    .timestamp {{
        font-size: 12.5px;
        color: rgba(255,255,255,0.75);
        margin-top: 10px;
    }}
    .page {{
        max-width: 1180px;
        margin: 0 auto;
        padding: 36px 40px 64px;
    }}
    .layout {{
        display: flex;
        gap: 24px;
        align-items: flex-start;
    }}
    .sidebar {{
        display: flex;
        flex-direction: column;
        gap: 12px;
        width: 250px;
        flex-shrink: 0;
    }}
    .stage-card {{
        background: var(--panel);
        border-radius: 12px;
        padding: 20px 22px;
        cursor: pointer;
        border: 1px solid transparent;
        transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
    }}
    .stage-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(26,26,30,0.08);
    }}
    .stage-card.active {{
        background: var(--red);
        box-shadow: 0 8px 24px rgba(237,48,36,0.28);
    }}
    .stage-card.pending {{
        background: var(--panel);
        border: 1px dashed var(--line);
    }}
    .stage-card.pending.active {{
        background: var(--panel);
        border: 1px dashed var(--pending);
        box-shadow: none;
    }}
    .stage-label {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 10px;
    }}
    .stage-card.active .stage-label {{
        color: rgba(255,255,255,0.85);
    }}
    .stage-count {{
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--ink);
        margin-bottom: 4px;
        font-variant-numeric: tabular-nums;
    }}
    .stage-card.active .stage-count {{
        color: #FFFFFF;
    }}
    .stage-card.pending .stage-count {{
        color: var(--pending);
    }}
    .stage-sublabel {{
        font-size: 12.5px;
        color: var(--muted);
    }}
    .stage-card.active .stage-sublabel {{
        color: rgba(255,255,255,0.8);
    }}
    .detail-panel {{
        flex: 1;
        background: var(--panel);
        border-radius: 14px;
        padding: 36px 40px;
        min-height: 340px;
    }}
    .detail-eyebrow {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: var(--red);
        text-transform: uppercase;
        margin-bottom: 10px;
    }}
    .detail-title {{
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.01em;
        margin-bottom: 8px;
    }}
    .detail-desc {{
        color: var(--muted);
        font-size: 14.5px;
        margin-bottom: 4px;
    }}
    .step-description {{
        color: var(--muted);
        font-size: 13.5px;
        margin-bottom: 22px;
        max-width: 540px;
        line-height: 1.55;
    }}
    .detail-table-chip {{
        display: inline-block;
        font-family: ui-monospace, "SF Mono", Consolas, monospace;
        font-size: 11.5px;
        background: #FFFFFF;
        border: 1px solid var(--line);
        padding: 5px 12px;
        border-radius: 20px;
        color: var(--muted);
        margin-bottom: 28px;
    }}
    .reading {{
        display: flex;
        gap: 40px;
        margin-bottom: 28px;
        flex-wrap: wrap;
    }}
    .reading-block {{
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px 26px;
        min-width: 220px;
    }}
    .reading-label {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .reading-value {{
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--red);
        font-variant-numeric: tabular-nums;
        line-height: 1;
    }}
    .reading-value.dim {{
        color: var(--pending);
        font-size: 22px;
    }}
    .section-title {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--ink);
        text-transform: uppercase;
        margin-bottom: 14px;
        padding-top: 24px;
        border-top: 1px solid var(--line);
    }}
    .ledger-row {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 10px 0;
        font-size: 14px;
        border-bottom: 1px solid var(--line);
    }}
    .ledger-row .num {{
        font-variant-numeric: tabular-nums;
        font-weight: 600;
    }}
    .ledger-row.total {{
        border-bottom: none;
        border-top: 2px solid var(--ink);
        margin-top: 4px;
        padding-top: 14px;
        font-weight: 800;
        font-size: 15px;
    }}
    .ledger-row.total .num {{
        color: var(--red);
        font-size: 17px;
    }}
    .ledger-op {{
        color: var(--pending);
        margin-right: 6px;
        font-weight: 700;
    }}
    .no-breakdown {{
        color: var(--muted);
        font-size: 13.5px;
        padding-top: 24px;
        border-top: 1px solid var(--line);
    }}
    .error-type-title {{
        display: flex;
        align-items: center;
        gap: 7px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--ink);
        text-transform: uppercase;
        margin-bottom: 14px;
        padding-top: 24px;
        border-top: 1px solid var(--line);
    }}
    .error-type-icon {{
        width: 15px;
        height: 15px;
        flex-shrink: 0;
    }}
    .error-type-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }}
    .error-type-chip {{
        display: flex;
        align-items: center;
        gap: 10px;
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 8px 14px 8px 10px;
    }}
    .error-type-chip .dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--red);
        flex-shrink: 0;
    }}
    .error-type-chip .label {{
        font-size: 13px;
        color: var(--ink);
    }}
    .error-type-chip .count {{
        font-size: 13px;
        font-weight: 700;
        color: var(--red);
        font-variant-numeric: tabular-nums;
    }}
</style>
</head>
<body>
    <div class="hero">
        <div class="hero-inner">
            <div class="title">Igloo Model</div>
            <div class="subtitle">Pipeline Health Overview</div>
            <div class="timestamp">Last generated: {generated_at}</div>
        </div>
    </div>

    <div class="page">
        <div class="layout">
            <div class="sidebar">{cards_html}
            </div>
            <div class="detail-panel" id="detail-panel"></div>
        </div>
    </div>

    <script>
        const STAGES = {stages_json};

        function fmt(n) {{
            return n === null || n === undefined ? "—" : n.toLocaleString();
        }}

        function selectStage(key) {{
            document.querySelectorAll(".stage-card").forEach(function(el) {{
                el.classList.remove("active");
            }});
            document.getElementById("card-" + key).classList.add("active");

            const stage = STAGES.find(function(s) {{ return s.key === key; }});
            const items = stage.breakdown_results || [];

            let reconcileHtml = "";
            if (stage.reconcile_from_key && items.length > 0) {{
                const fromStage = STAGES.find(function(s) {{ return s.key === stage.reconcile_from_key; }});
                if (fromStage && fromStage.available) {{
                    reconcileHtml = '<div class="section-title">Reconciliation</div>'
                        + '<div class="ledger-row"><span>' + fromStage.label + ' Total</span><span class="num">' + fmt(fromStage.count) + '</span></div>';

                    // running total: subtract each exclusion, only when its
                    // count is actually available (so an n/a item doesn't
                    // silently corrupt the variance math below)
                    let runningTotal = fromStage.count;
                    let allItemsAvailable = true;
                    items.forEach(function(item) {{
                        const val = item.available ? fmt(item.count) : "n/a";
                        reconcileHtml += '<div class="ledger-row"><span><span class="ledger-op">−</span>' + item.name + '</span><span class="num">' + val + '</span></div>';
                        if (item.available) {{
                            runningTotal -= item.count;
                        }} else {{
                            allItemsAvailable = false;
                        }}
                    }});

                    // Unaccounted Variance: the gap between what the
                    // subtraction predicts and the real ending total —
                    // shown explicitly rather than hidden, same pattern
                    // as the Mosaic dashboard's own reconciliation boxes.
                    if (allItemsAvailable && stage.available) {{
                        const variance = stage.count - runningTotal;
                        if (variance !== 0) {{
                            const sign = variance > 0 ? "+" : "−";
                            reconcileHtml += '<div class="ledger-row"><span>Unaccounted Variance</span><span class="num">' + sign + fmt(Math.abs(variance)) + '</span></div>';
                        }}
                    }}

                    const endLabel = stage.available ? fmt(stage.count) : "Not yet available";
                    reconcileHtml += '<div class="ledger-row total"><span>= ' + stage.label + ' Total</span><span class="num">' + endLabel + '</span></div>';
                }}
            }}

            let breakdownHtml = "";
            if (!reconcileHtml) {{
                if (items.length === 0) {{
                    breakdownHtml = '<div class="no-breakdown">No breakdown defined for this stage yet.</div>';
                }} else {{
                    breakdownHtml = '<div class="section-title">Breakdown</div>';
                    items.forEach(function(item) {{
                        const val = item.available ? fmt(item.count) : "n/a";
                        breakdownHtml += '<div class="ledger-row"><span>' + item.name + '</span><span class="num">' + val + '</span></div>';
                    }});
                }}
            }}

            // --- Error type breakdown: a variable-length list (however many
            // distinct error types exist), shown as pill badges rather than
            // ledger rows so it's visually distinct from the reconciliation
            // math above it. Requested by Melissa: "add the error types we
            // found and how many records of each" — added 8/5.
            let errorTypeHtml = "";
            const errorTypes = stage.error_type_breakdown || [];
            if (errorTypes.length > 0) {{
                const warningIcon = '<svg class="error-type-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v4M12 17h.01M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>';
                errorTypeHtml = '<div class="error-type-title">' + warningIcon + ' Error Types</div>'
                    + '<div class="error-type-grid">';
                errorTypes.forEach(function(item) {{
                    errorTypeHtml += '<div class="error-type-chip"><span class="dot"></span><span class="label">' + item.name + '</span><span class="count">' + fmt(item.count) + '</span></div>';
                }});
                errorTypeHtml += '</div>';
            }}

            const countDisplay = stage.available ? fmt(stage.count) : "Not yet available";
            const valueClass = stage.available ? "reading-value" : "reading-value dim";
            const descriptionHtml = stage.description
                ? '<div class="step-description">' + stage.description + '</div>'
                : "";

            document.getElementById("detail-panel").innerHTML =
                '<div class="detail-eyebrow">' + stage.label.toUpperCase() + '</div>'
                + '<div class="detail-title">' + stage.label + '</div>'
                + '<div class="detail-desc">' + stage.sublabel + '</div>'
                + descriptionHtml
                + '<div class="detail-table-chip">' + stage.table + '</div>'
                + '<div class="reading">'
                    + '<div class="reading-block">'
                        + '<div class="reading-label">Record Count</div>'
                        + '<div class="' + valueClass + '">' + countDisplay + '</div>'
                    + '</div>'
                + '</div>'
                + reconcileHtml
                + breakdownHtml
                + errorTypeHtml;
        }}

        selectStage("{default_key}");
    </script>
</body>
</html>
"""

def main():
    print("Connecting to SQL Server...")
    conn = get_connection()

    print("Querying stage tables...")
    stage_counts = get_counts(conn)
    conn.close()

    generated_at = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
    html = render_html(stage_counts, generated_at)

    with open(config.OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Done. Wrote {config.OUTPUT_HTML}")
    for stage in stage_counts:
        if stage["available"]:
            print(f"  {stage['label']:<22} {stage['count']:,}")
        else:
            print(f"  {stage['label']:<22} Not yet available")


if __name__ == "__main__":
    main()
