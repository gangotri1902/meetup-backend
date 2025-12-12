import math
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

def flatten_randomuser(user):
    try:
        uid=user.get("login",{}).get("uuid")
        email=user.get("email")
        first_name=user.get("name",{}).get("first")
        last_name=user.get("name",{}).get("last")
        gender=user.get("gender")
        lat=float(user.get("location",{}).get("coordinates",{}).get("latitude"))
        lon=float(user.get("location",{}).get("coordinates",{}).get("longitude"))
        if not uid or not email or lat is None or lon is None:
            return None
        return{
          "uid":str(uid),
           "email":str(email),
           "first_name":first_name if first_name is not None else "",
           "last_name":last_name if last_name is not None else "",
           "gender":gender if gender is not None else "",
           "latitude":lat,
           "longitude":lon 
        }
    except Exception:
        return None
    
def generate_run_id():
   return "RUN_" + uuid.uuid4().hex[:12]
     
    
    
    


