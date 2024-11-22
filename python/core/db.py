import sqlite3
import os
from core.logger import *

def initdb():
    logger = get_logger()
    db_dir = os.getcwd() + '/db'
    db_file = db_dir + '/internal.db'
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)
    try:
        logger.info(f'Using internal DB {db_file}')
        conn = sqlite3.connect(db_file) 
        if is_db_populated(conn) : 
            pass
        else:
            populatedb(conn)
    except:
        logger.info(f'Unable to use internal DB')
    
def populatedb(conn):
    sql_inittable = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            jobname text NOT NULL, 
            start_time TEXT, 
            end_time TEXT,
            status TEXT
        );"""
    
    cursor = conn.cursor()
    cursor.execute(sql_inittable) 
    conn.commit()
    
def is_db_populated (conn):
    sql_check = """SELECT count(*) FROM sqlite_master WHERE type='table' AND name='jobs';""" 
    cursor = conn.cursor()
    cursor.execute(sql_check) 
    rows = cursor.fetchall()  
    if rows[0][0] == 1:
        return True
    else:
        return False

def startjob(jobrun, name, time):
    db_dir = os.getcwd() + '/db'
    db_file = db_dir + '/internal.db'
    conn = sqlite3.connect(db_file) 
    cursor = conn.cursor()
    sql_insert =  f"""INSERT INTO jobs (run_id, jobname, start_time, end_time, status) VALUES ('{jobrun}', '{name}', '{time}', NULL, 'Running')"""
    cursor.execute(sql_insert)
    conn.commit()
    conn.close() 

def update_job(jobrun, status, time):
    db_dir = os.getcwd() + '/db'
    db_file = db_dir + '/internal.db'
    conn = sqlite3.connect(db_file) 
    cursor = conn.cursor()
    sql_insert =  f"""UPDATE jobs SET status =  '{status}', end_time = '{time}' WHERE run_id = '{jobrun}'"""
    cursor.execute(sql_insert)
    conn.commit()
    conn.close() 

    