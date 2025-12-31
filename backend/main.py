from fastapi import FastAPI,HTTPException,Query
from datetime import datetime,timezone
from typing import Dict,List
import requests
import sqlite3
from . import crud
from . import utils


app=FastAPI(title="Meetup Backend")

@app.get("/")
def simple_check()->Dict[str,str]:
    return {"status":"ok","message":"Meetup Backend running"}

@app.post("/ingest")                
def ingest_users(count: int)->Dict:
    connection = crud.get_connection()
    try:
        crud.create_users_table(connection)

        api_url = f"https://randomuser.me/api/?results={count}"
        try:
            response = requests.get(api_url, timeout=15)
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Error calling RandomUser API: {str(e)}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"RandomUser API returned status {response.status_code}"
            )

        data = response.json()
        raw_users = data.get("results", [])

        run_id = utils.generate_run_id()
        ingested_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

        inserted_count = 0
        skipped_count = 0

        for raw_user in raw_users:
            flattened_user = utils.flatten_randomuser(raw_user)
            if flattened_user is None:
                skipped += 1
                continue

            flattened_user["run_id"] = run_id
            flattened_user["ingested_at"] = ingested_at

            try:
                crud.insert_user(connection, flattened_user)
                inserted_count += 1
            except sqlite3.IntegrityError:
                skipped_count += 1
                continue

        total_users = crud.count_users(connection)

    finally:
        connection.close()

    return {
        "requested": count,
        "inserted": inserted_count,
        "skipped": skipped_count,
        "run_id": run_id,
        "ingested_at": ingested_at,
        "total_in_db": total_users,
    }
    
    
@app.get("/random-user")   
def get_randomuser()->Dict:
    connection=crud.get_connection()
    try:
        user=crud.get_random_user(connection)
        if not user:
            raise HTTPException(status_code=404, detail="No users in db")
        return user
    finally:
        connection.close()
                          
@app.get("/nearest")
def nearest_users(
    uid: str | None = None,
    email: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
) -> Dict:
    if not uid and not email:
        raise HTTPException(
            status_code=400,
            detail="Provide either uid or email as identifier."
        )

    connection = crud.get_connection()
    try:
        target_user = (
            crud.get_user_by_uid(connection, uid)
            if uid
            else crud.get_user_by_email(connection, email)
        )

        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")

        candidates = crud.get_all_users_except_uid(
            connection, target_user["uid"]
        )

    finally:
        connection.close()

    target_latitude = float(target_user["latitude"])
    target_longitude = float(target_user["longitude"])

    distance_entries: List[tuple] = []

    for candidate in candidates:
        try:
            candidate_latitude = float(candidate["latitude"])
            candidate_longitude = float(candidate["longitude"])
        except (TypeError, ValueError):
            continue

        distance_km = utils.haversine(
            target_latitude,
            target_longitude,
            candidate_latitude,
            candidate_longitude,
        )

        entry = candidate.copy()
        entry["distance_km"] = round(distance_km, 4)
        distance_entries.append((distance_km, entry))

    distance_entries.sort(key=lambda item: item[0])

    nearest_list = [entry for _, entry in distance_entries[:limit]]

    return {
        "target": target_user,
        "nearest": nearest_list,
    }


        
@app.get("/search")        
def search_users(q:str,limit:int=10)->Dict:
    if not q.strip():
        return{
            "query":q,
            "count":0,
            "results":[]
        }
    query=q.strip().lower()  
    
    connection=crud.get_connection() 
    try:
        users=crud.get_all_users(connection) 
     

    finally:
        connection.close()    
    results:List[Dict]=[]    
    for user in users:
        score=utils.calculate_score(user,query)
     

        if score>0:
            entry=user.copy()
            entry["search_score"]=score
            results.append(entry)
            
    results.sort(key=lambda x:x["search_score"])  
        
        
    return{
            "query":q,
            "count":len(results),
            "results":results[:limit]
        } 
    
    
    
@app.get("/recommend")    
def recommend_users(uid:str,limit:int=Query(10,ge=1,le=100))->Dict: 
    connection=crud.get_connection()
    try:
        target_user=crud.get_user_by_uid(connection,uid)
        if not target_user:
            raise HTTPException(status_code=404,detail="Target user not found")
        candidates=crud.get_all_users_except_uid(connection,uid)
    finally:
        connection.close()    
        
    weights={
        "distance":1.0,
        "age":0.6,
        "nationality":0.3,
        "name":0.2    }    
    
    recommendations:List[Dict]=[]
    
    target_latitude=float(target_user["latitude"])
    target_longitude=float(target_user["longitude"])
  

    target_age=utils.calculate_age(target_user["dob"])
    
    for candidate in candidates:
        try:
            candidate_latitude=float(candidate["latitude"])
            candidate_longitude=float(candidate["longitude"])
        except Exception:
            continue  
        
       

        distance_km=utils.haversine(target_latitude,
                                    target_longitude,
                                    candidate_latitude,
                                    candidate_longitude)   
        if distance_km >500:
            continue
        candidate_age=utils.calculate_age(candidate["dob"]) 
        age_difference=abs(target_age-candidate_age)
    
        same_nationality=target_user["nat"]==candidate["nat"]
    
        score=utils.final_reccomendation_score(
        distance_km=distance_km,
        age_diff=age_difference,
        same_nat=same_nationality,
        name1=target_user["first_name"],
        name2=candidate["first_name"],
        weights=weights
        
        )
    
        entry=candidate.copy()
        entry["distance_km"]=round(distance_km,2)
        entry["recommendation_score"]=score
        recommendations.append(entry)
    
    recommendations.sort(key=lambda x:x["recommendation_score"] ,reverse=True)
    
    return{
        "Target_user":target_user,
        "count":len(recommendations),
        "recommendations":recommendations[:limit]
        
    }

