import sqlite3
import random

DB_PATH="users.db"

def get_connection(db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    conn.row_factory=sqlite3.Row
    return conn

def create_users_table(conn):
    cur=conn.cursor()
    cur.execute("""
     CREATE TABLE IF NOT EXISTS users(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         uid TEXT,
         email TEXT,
         first_name TEXT,
         last_name  TEXT,
         gender TEXT,
         latitude REAL,
         longitude REAL,
         run_id TEXT,
         ingested_at TEXT
     )                 
                """)
    conn.commit()
    
def insert_user(conn,user):
        cur=conn.cursor()
        cur.execute("""
         INSERT INTO users(
             uid,email,first_name,last_name,gender,latitude,longitude,run_id,ingested_at
         )   
         VALUES(?,?,?,?,?,?,?,?,?)        
                    """,(
                        user["uid"],
                        user["email"],
                        user.get("first_name",""),
                        user.get("last_name",""),
                        user.get("gender",""),
                        user["latitude"],
                        user["longitude"],
                        user.get("run_id"),
                        user.get("ingested_at"),
                    ),
                )
        conn.commit()
        
def insert_many_users(conn,users):
    cur=conn.cursor()
    rows_toinsert=[
         (
            u["uid"],
            u["email"],
            u.get("first_name", ""),
            u.get("last_name", ""),
            u.get("gender", ""),
            u["latitude"],
            u["longitude"],
            u.get("run_id"),
            u.get("ingested_at"),
        )
        for u in users
    ]
    cur.executemany("""
           INSERT INTO users(
               uid,email,first_name,last_name,gender,latitude,longitude,run_id,ingested_at
           ) VALUES(?,?,?,?,?,?,?,?,?)        
                    """,rows_toinsert,)  
    conn.commit()
    return len(rows_toinsert)  

def row_to_dict(row):
    return dict(row)


def get_all_users(conn):
    cur=conn.cursor()
    cur.execute("SELECT * FROM users")
    rows=cur.fetchall()
    return [row_to_dict(r) for r in rows]
 
 

def get_user_by_uid(conn,uid):
    cur=conn.cursor()
    cur.execute("SELECT * FROM users WHERE uid=?",(uid,))
    row=cur.fetchone()
    return row_to_dict(row) if row else None

def get_user_by_email(conn,email):
    cur=conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=?",(email,))
    row=cur.fetchone()
    return row_to_dict(row) if row else None

def count_users(conn):
    cur=conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM users")
    row=cur.fetchone()
    return int(row["c"]) if row else 0

def get_random_user(conn):
    cur=conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY RANDOM() LIMT 1")
    row=cur.fetchone()
    return row_to_dict(row) if row else None

def get_all_users_except_uid(conn,uid):
    cur=conn.cursor()
    cur.execute("SELECT * FROM users WHERE uid!=?",(uid,))
    rows=cur.fetchall()
    return [row_to_dict(r) for r in rows]

    


        
        
    
    
