"""Read-only log projection; pipe directly to replay_failed_results.mjs.

Never writes the OpenCode database, client messages, or saved report.
"""
import json
import sqlite3
from pathlib import Path

session = 'ses_e268b4568ffeHoOHcgUOBosB0C'
db = Path.home() / '.local/share/opencode/opencode.db'
with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True) as connection:
    rows = connection.execute(
        'select data from part where session_id=? order by time_created,id', (session,)
    ).fetchall()
parts = [json.loads(row[0]) for row in rows]
failed = [p['state']['input'] for p in parts
          if p.get('tool') == 'liuren_adjudication_result'
          and p.get('state', {}).get('status') == 'error']
print(json.dumps({'session': session, 'failed_results': failed}))
