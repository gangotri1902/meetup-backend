import math
import uuid
from datetime import datetime
from typing import Dict,Optional


def haversine(source_latitude:float,
              source_longitude:float,
              target_latitude:float,
              target_longitude:float)->float:
    
    EARTH_RADIUS_KM = 6371.0
    
    lat1=math.radians(source_latitude)
    lon1=math.radians(source_longitude)
    lat2=math.radians(target_latitude)
    lon2=math.radians(target_longitude)
    
    delta_lat=lat2-lat1
    dleta_lon=lon2-lon1
    
   
    
    a = (math.sin(delta_lat/2)**2 +
         math.cos(lat1)*math.cos(lat2)*math.sin(dleta_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return EARTH_RADIUS_KM * c



def flatten_randomuser(user: Dict) -> Optional[Dict]:
    try:
       
        login = user.get("login", {})
        name = user.get("name", {})
        location = user.get("location", {})
        coordinates = location.get("coordinates", {})
        dob_info=user.get("dob",{})

        uid = login.get("uuid")
        email = user.get("email")
        dob_iso=dob_info.get("date")
        nationality=user.get("nat")
        latitude_raw = coordinates.get("latitude")
        longitude_raw = coordinates.get("longitude")
       
        if not all([uid, email, dob_iso, nationality, latitude_raw, longitude_raw]):    
            return None

        try:
            latitude = float(latitude_raw)
            longitude = float(longitude_raw)
        except (ValueError, TypeError):
            return None

        return {
            "uid": str(uid),
            "email": str(email),
            "first_name": name.get("first", "") or "",
            "last_name":  name.get("last", "") or "",
            "gender": user.get("gender", "") or "",
            "profile_pic":user.get("picture",{}).get("medium",""),
            "dob":dob_iso,
            "nat":nationality,
            "latitude": latitude,
            "longitude": longitude
        }
    except Exception:
        return None
    
def generate_run_id()->str:
   return "RUN_" + uuid.uuid4().hex[:12]




def search_name_score(user: Dict, query: str) -> int:
    query = query.lower().strip()

    first_name = user.get("first_name", "").lower()
    last_name = user.get("last_name", "").lower()

    

    if first_name.startswith(query):
        return 100 + len(query)

    if last_name.startswith(query):
        return 90 + len(query)

    return 0

def calculate_age(dob_iso:str)->int:
    birth_year=int(dob_iso[:4])
    current_year=datetime.utcnow().year
    return current_year - birth_year


def name_similarity_score(name_a:str,name_b:str)->int:
    vowels=set("aeiou")
    vowels_a=set(name_a.lower())& vowels
    vowels_b=set(name_b.lower()) & vowels
    return len(vowels_a & vowels_b)*2

def distance_score(distance_km:float)->int:
    if distance_km<=10:
        return 100
    if distance_km<=50:
        return 70
    if distance_km<=100:
        return 50
    if distance_km<=200:
        return 30

    return 0
    


def age_simialrity_score(age_difference:int)->int:
    if age_difference<=2:
        return 20
    if age_difference<=5:
        return 15
    if age_difference<=10:
        return 8
    if age_difference<=20:
        return 2
    
    return 0
   

def nationality_score(target_nat:str,candidate_nat:str)->int:
    return 10 if target_nat==candidate_nat else 0

def final_reccomendation_score(distance_km:float,age_difference:int,same_nationality:bool,target_name:str,candidate_name:str,weights:Dict[str,float])->float:
    score=0.0
    
    score+=weights["distance"]*distance_score(distance_km)
    score+=weights["age"]*age_simialrity_score(age_difference)
    score+=weights["nationality"]*(10 if same_nationality else 0)
    score+=weights["name"]*name_similarity_score(target_name,candidate_name)
    
    return round(score,2)



    
    
    


