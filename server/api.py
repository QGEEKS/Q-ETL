from fastapi import FastAPI
import sqlite3
from datetime import datetime
import uvicorn
from pathlib import Path
import subprocess

def get_db_dir():
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    internal_db_path = parent_dir / 'db' / 'internal.db'
    return internal_db_path

def get_db_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

db_dir = get_db_dir()

app = FastAPI()

@app.get('/jobs')
def read_jobs():
    conn = get_db_connection(db_dir)
    jobs = conn.execute('SELECT * FROM jobs').fetchall()
    jobs_list = [dict(job) for job in jobs]
    sorted_jobs_list = sorted(jobs_list, key=lambda x: datetime.fromisoformat(x['start_time']), reverse=True)
    conn.close()
    return sorted_jobs_list

@app.get('/run_code/{script_name}')
def run_code(script_name: str):
    allowed_scripts = ['development']
    if script_name in allowed_scripts:
        cmd_path = Path(__file__).parent.parent / f'{script_name}.cmd'
        result = subprocess.run([cmd_path], capture_output=True, text=True)
        if result.returncode == 0:
            return {
                'message': f'{script_name}.cmd ran succesfully'
            }
        else:
            return {
                'message': f'{script_name}.cmd failed to run!'
            }
    else:
        return {
            'message': f'The file {script_name}.cmd either does not exist or you are not permitted to run the script.'
        }


if __name__ == '__main__':
    uvicorn.run('api:app', host='localhost', port=8080, reload=True)