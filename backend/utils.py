import math
from typing import Optional,Dict,Any


def haversine(lat1:float,lon1:float,lat2:float,lon2:float) -> float:
    R = 6371.0
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(d_phi/2)**2 +
         math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def flatten_randomuser(user:Dict[str,Any]) -> Optional[Dict[str,Any]]:
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
    
    


