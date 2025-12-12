from fastapi import FastAPI,HTTPException,Query
from datetime import datetime,timezone
import requests
from . import crud
from . import utils

app=FastAPI(title="Meetup Backend",debug=True)

@app.get("/")
def simple_check():
    return {"status":"ok","message":"Meetup Backend running"}

@app.post("/ingest")
def ingest_users(count:int):
    conn=crud.get_connection()
    try:
        crud.create_users_table(conn)
        url=f"https://randomuser.me/api/?results={count}"
        try:
            response=requests.get(url,timeout=15)
        except requests.RequestException as e:
            conn.close() 
            raise HTTPException(status_code=502,detail=f"Error calling RandomUser API:{str(e)}")   
        if response.status_code !=200:
            conn.close()
            raise HTTPException(status_code=502,detail=f"RandomUser API returned status {response.status_code}")
        data=response.json()
        raw_users=data.get("results",[])
        
        run_id=utils.generate_run_id()
        ingested_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

        rows_to_insert=[]
        skipped=0
        
        for raw in raw_users:
            flat=utils.flatten_randomuser(raw)
            if flat is None:
                skipped+=1
                continue
            flat["run_id"]=run_id
            flat["ingested_at"]=ingested_at
            rows_to_insert.append(flat)
            
        inserted=0
        if rows_to_insert:
            inserted=crud.insert_many_users(conn,rows_to_insert) 
        total=crud.count_users(conn)       
        
    finally:
        try:
            conn.close()
        except Exception:
            pass
        
    return {
        "requested": count,
        "inserted":inserted,
        "skipped":skipped,
        "run_id":run_id,
        "ingested_at":ingested_at,
        "total_in_db":total,
    }  
    
    
    
@app.get("/random-user")   
def get_randomuser():
    conn=crud.get_connection()
    try:
        user=crud.get_random_user(conn)
        if not user:
            raise HTTPException(status_code=404, detail="No users in db")
        return user
    finally:
        conn.close()
                          
@app.get("/nearest")
def nearest_users(uid = None, email = None, limit: int = Query(100, ge=1, le=1000)):
   
    if not uid and not email:
        raise HTTPException(status_code=400, detail="Provide either uid or email as identifier.")

    conn = crud.get_connection()
    try:
        
        target = None
        if uid:
            target = crud.get_user_by_uid(conn, uid)
        elif email:
            target = crud.get_user_by_email(conn, email)

        if not target:
            raise HTTPException(status_code=404, detail="Target user not found in database.")

        
        others = crud.get_all_users_except_uid(conn, target["uid"])

        distances = []
        tlat = float(target["latitude"])
        tlon = float(target["longitude"])
        for u in others:
            try:
                ulat = float(u["latitude"])
                ulon = float(u["longitude"])
            except Exception:
               
                continue
            d = utils.haversine(tlat, tlon, ulat, ulon)
            
            entry = u.copy()
            entry["distance_km"] = round(d, 4)
            distances.append((d, entry))

        distances.sort(key=lambda x: x[0])

        
        nearest_list = [item for _, item in distances[:limit]]

        return {"target": target, "nearest": nearest_list}

    finally:
        conn.close()


