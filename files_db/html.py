"""
Igloo Pipeline Dashboard — basic version

Run this script to pull current row counts from each stage table in SQL
Server and regenerate the dashboard HTML file. Open the HTML file in your
browser to see the latest numbers. Re-run any time you want it to update.

Requires: pip install pyodbc
"""

import datetime
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
    """Query row count for each configured stage table.

    If a table doesn't exist yet (e.g. Silver/Gold not built out yet),
    that stage is marked as not available instead of failing the whole run.
    """
    counts = []
    cursor = conn.cursor()
    for stage in config.STAGES:
        try:
            query = f"SELECT COUNT(*) FROM {stage['table']}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            counts.append({**stage, "count": count, "available": True})
        except pyodbc.Error:
            # Table doesn't exist yet, or isn't accessible — skip gracefully
            conn.rollback()  # clear the failed transaction so the next query can run
            counts.append({**stage, "count": None, "available": False})
    return counts


def render_html(stage_counts, generated_at):
    # Last *available* stage gets the highlighted "active" styling
    last_available_idx = max(
        (i for i, s in enumerate(stage_counts) if s["available"]), default=-1
    )

    cards_html = ""
    for i, stage in enumerate(stage_counts):
        active_class = " active" if i == last_available_idx else ""
        if stage["available"]:
            count_html = f"{stage['count']:,}"
            sublabel_html = stage["sublabel"]
        else:
            active_class += " pending"
            count_html = "—"
            sublabel_html = "Not yet available"
        cards_html += f"""
        <div class="stage-card{active_class}">
            <div class="stage-label">{stage['label'].upper()}</div>
            <div class="stage-count">{count_html}</div>
            <div class="stage-sublabel">{sublabel_html}</div>
        </div>"""

    rows_html = ""
    for stage in stage_counts:
        count_display = f"{stage['count']:,}" if stage["available"] else "Not yet available"
        rows_html += f"""
        <tr>
            <td>{stage['label']}</td>
            <td class="mono">{stage['table']}</td>
            <td class="num">{count_display}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Igloo — Pipeline Health Overview</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: #fafafa;
        color: #1a1a2e;
        padding: 40px;
    }}
    .header {{
        margin-bottom: 32px;
    }}
    .title {{
        font-size: 28px;
        font-weight: 700;
    }}
    .title span {{
        color: #6b46c1;
    }}
    .subtitle {{
        color: #6b7280;
        font-size: 14px;
        margin-top: 4px;
    }}
    .timestamp {{
        color: #9ca3af;
        font-size: 12px;
        margin-top: 8px;
    }}
    .stage-row {{
        display: flex;
        gap: 16px;
        margin-bottom: 40px;
        flex-wrap: wrap;
    }}
    .stage-card {{
        background: #1e2130;
        color: white;
        border-radius: 10px;
        padding: 20px 24px;
        min-width: 200px;
        flex: 1;
    }}
    .stage-card.active {{
        background: linear-gradient(135deg, #6b46c1, #9333ea);
    }}
    .stage-card.pending {{
        background: #e5e7eb;
        color: #6b7280;
    }}
    .stage-card.pending.active {{
        background: #e5e7eb;
    }}
    .stage-label {{
        font-size: 11px;
        letter-spacing: 0.05em;
        opacity: 0.7;
        margin-bottom: 8px;
    }}
    .stage-count {{
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 4px;
    }}
    .stage-sublabel {{
        font-size: 12px;
        opacity: 0.6;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    th, td {{
        text-align: left;
        padding: 14px 20px;
        border-bottom: 1px solid #eee;
        font-size: 14px;
    }}
    th {{
        background: #f3f4f6;
        font-size: 11px;
        letter-spacing: 0.05em;
        color: #6b7280;
        text-transform: uppercase;
    }}
    td.mono {{
        font-family: "SF Mono", Consolas, monospace;
        font-size: 12px;
        color: #6b7280;
    }}
    td.num {{
        font-weight: 600;
        text-align: right;
    }}
</style>
</head>
<body>
    <div class="header">
        <div class="title">Igloo <span>Model</span></div>
        <div class="subtitle">Pipeline Health Overview</div>
        <div class="timestamp">Last generated: {generated_at}</div>
    </div>

    <div class="stage-row">{cards_html}
    </div>

    <table>
        <thead>
            <tr>
                <th>Stage</th>
                <th>Source Table</th>
                <th style="text-align:right">Record Count</th>
            </tr>
        </thead>
        <tbody>{rows_html}
        </tbody>
    </table>
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
        print(f"  {stage['label']:<22} {stage['count']:,}")


if __name__ == "__main__":
    main()