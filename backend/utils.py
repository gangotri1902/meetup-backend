import math
from typing import Optional,Dict,Any
from datetime import datetime
import uuid


def haversine(lat1,lon1,lat2,lon2):
    R = 6371.0
    
    lat1=math.radians(lat1)
    lon1=math.radians(lon1)
    lat2=math.radians(lat2)
    lon2=math.radians(lon2)
    
    dlat=lat2-lat1
    dlon=lon2-lon1
    
   
    
    a = (math.sin(dlat/2)**2 +
         math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def flatten_randomuser(user: dict) -> dict | None:
    try:
       
        login = user.get("login", {})
        name = user.get("name", {})
        location = user.get("location", {})
        coordinates = location.get("coordinates", {})

        uid = login.get("uuid")
        email = user.get("email")
        lat_str = coordinates.get("latitude")
        lon_str = coordinates.get("longitude")

      
        if not uid or not email or lat_str is None or lon_str is None:
            return None

        try:
            latitude = float(lat_str)
            longitude = float(lon_str)
        except (ValueError, TypeError):
            return None

        return {
            "uid": str(uid),
            "email": str(email),
            "first_name": name.get("first", "") or "",
            "last_name":  name.get("last", "") or "",
            "gender": user.get("gender", "") or "",
            "latitude": latitude,
            "longitude": longitude
        }
    except Exception:
        return None
    
def generate_run_id():
   return "RUN_" + uuid.uuid4().hex[:12]
     
    
    
    


