import sqlite3
import json
import os
from .schemas import TraceLog

DB_PATH = os.getenv("TRACE_DB_PATH", "traces.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            workflow_state TEXT,
            agent TEXT,
            input_data TEXT,
            output_data TEXT,
            rejected_options TEXT,
            latency_ms REAL,
            cost_usd REAL,
            tokens INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_trace(trace: TraceLog):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO traces (run_id, workflow_state, agent, input_data, output_data, rejected_options, latency_ms, cost_usd, tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trace.run_id,
        trace.workflow_state,
        trace.agent,
        json.dumps(trace.input_data),
        json.dumps(trace.output_data),
        json.dumps(trace.rejected_options),
        trace.latency_ms,
        trace.cost_usd,
        trace.tokens
    ))
    conn.commit()
    conn.close()

def get_traces(run_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM traces WHERE run_id = ? ORDER BY id ASC', (run_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

init_db()
