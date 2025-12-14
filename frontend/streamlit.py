import streamlit as st
import requests
import pandas as pd

BACKEND_URL="http://127.0.0.1:8000"

st.set_page_config(page_title="Meetup App",layout="centered")
st.title("Meetup Users")

if "target_user" not in st.session_state:
    st.session_state.target_user=None
if "nearest_users" not in st.session_state:
    st.session_state.nearest_users=[]  
    
if st.button("Pick a   Random User") :
    try:
        response=requests.get(f"{BACKEND_URL}/random-user",timeout=5)  
        if response.status_code==200:
            st.session_state.target_user=response.json() 
            st.session_state.nearest_users=[]
        else:
            st.error(f"Backend error:{response.status_code}")    
    except requests.RequestException as e:
        st.error(f"Cannot connect to backend:{e}")      
        
if st.session_state.target_user:
    user=st.session_state.target_user
    st.subheader("🎯 Selected User")
    st.write(f"**Name:** {user['first_name']} {user['last_name']}")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**Gender:** {user['gender']}")
    st.write(f"**Latitude:** {user['latitude']}")
    st.write(f"**Longitude:** {user['longitude']}")
    
    if st.button("Find Nearest Users"):
        try:
            response=requests.get(f"{BACKEND_URL}/nearest",params={
                "uid":user["uid"],
                "limit":100
            },
                                  timeout=10)
              
            if response.status_code==200:
               st.session_state.nearest_users=response.json()["nearest"] 
            else:
                st.error(f"Backend error:{response.status_code}")  
        except requests.RequestException as e:
            st.error(f"Cannot connect to backend:{e}")  
            
if st.session_state.target_user and st.session_state.nearest_users:
    st.subheader("Nearby Users Map")  
    target=st.session_state.target_user
    nearest=st.session_state.nearest_users
    
    rows=[]    
    
    rows.append({
        "lat":target["latitude"],
        "lon":target["longitude"],
        "type":"Target User"
    })  
    
    for u in nearest:
        rows.append({
            "lat":u["latitude"],
            "lon":u["longitude"],
            "type":"Nearby User"
        })  
    
    df=pd.DataFrame(rows)
    
    st.map(df)
          
                   
                 