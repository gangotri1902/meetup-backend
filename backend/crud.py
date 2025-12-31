import sqlite3
from typing import Dict,List,Optional


DB_PATH:str="users.db"

def get_connection(db_path:str=DB_PATH)->sqlite3.Connection:
    connection=sqlite3.connect(db_path)
    connection.row_factory=sqlite3.Row
    return connection

def create_users_table(connection:sqlite3.Connection)->None:
    cursor=connection.cursor()
    cursor.execute("""
     CREATE TABLE IF NOT EXISTS users(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         uid TEXT,
         email TEXT UNIQUE,
         first_name TEXT,
         last_name  TEXT,
         gender TEXT,
         profile_pic TEXT,
         dob TEXT,
         nat TEXT,
         latitude REAL,
         longitude REAL,
         run_id TEXT,
         ingested_at TEXT
     )                 
                """)
    connection.commit()
    
def insert_user(connection:sqlite3.Connection,user:dict)->None:
        cursor=connection.cursor()
        cursor.execute("""
         INSERT INTO users(
             uid,email,first_name,last_name,gender,profile_pic,dob,nat,latitude,longitude,run_id,ingested_at
         )   
         VALUES(?,?,?,?,?,?,?,?,?,?,?,?)        
                    """,(
                        user["uid"],
                        user["email"],
                        user.get("first_name",""),
                        user.get("last_name",""),
                        user.get("gender",""),
                        user.get("profile_pic",""),
                        user.get("dob",""),
                        user.get("nat",""),
                        user["latitude"],
                        user["longitude"],
                        user.get("run_id"),
                        user.get("ingested_at"),
                        ),
                )
        connection.commit()
        
def insert_many_users(connection:sqlite3.Connection,users:List[Dict])->int:
    cursor=connection.cursor()
    rows_toinsert=[
         (
            user["uid"],
            user["email"],
            user.get("first_name", ""),
            user.get("last_name", ""),
            user.get("gender", ""),
            user.get("profile_pic",""),
            user.get("dob",""),
            user.get("nat",""),
            user["latitude"],
            user["longitude"],
            user.get("run_id"),
            user.get("ingested_at"),
        )
        for user in users
    ]
    cursor.executemany("""
           INSERT INTO users(
               uid,email,first_name,last_name,gender,profile_pic,dob,nat,latitude,longitude,run_id,ingested_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)        
                    """,rows_toinsert,)  
    connection.commit()
    return len(rows_toinsert)  

def row_to_dict(row:sqlite3.Row)->Dict:
    return dict(row)


def get_all_users(connection:sqlite3.Connection)->List[Dict]:
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows=cursor.fetchall()
    return [row_to_dict(row) for row in rows]
 
 

def get_user_by_uid(connection:sqlite3.Connection,uid:str)->Optional[Dict]:
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM users WHERE uid=?",(uid,))
    row=cursor.fetchone()
    return row_to_dict(row) if row else None

def get_user_by_email(connection:sqlite3.Connection,email:str)->Optional[Dict]:
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?",(email,))
    row=cursor.fetchone()
    return row_to_dict(row) if row else None

def count_users(connection:sqlite3.Connection)->int:
    cursor=connection.cursor()
    cursor.execute("SELECT COUNT(*) AS c FROM users")
    row=cursor.fetchone()
    return int(row["count"]) if row else 0

def get_random_user(connection:sqlite3.Connection)->Optional[Dict]:
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM users ORDER BY RANDOM() LIMIT 1")
    row=cursor.fetchone()
    return row_to_dict(row) if row else None

def get_all_users_except_uid(connection:sqlite3.Connection,uid:str)->List[Dict]:
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM users WHERE uid!=?",(uid,))
    rows=cursor.fetchall()
    return [row_to_dict(row) for row in rows]

    


        
        
    
    
