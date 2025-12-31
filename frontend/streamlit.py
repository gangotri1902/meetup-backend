
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium



BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Meetup App", layout="centered")
st.title("Meetup Users")


if "target_user" not in st.session_state:
    st.session_state.target_user = None
    
if "user_selected" not in st.session_state:
    st.session_state.user_selected = False
    

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "recommend_fetched" not in st.session_state:
    st.session_state.recommend_fetched = False

if "search_query" not in st.session_state:
    st.session_state.search_query = ""





st.subheader("🔍 Search Users")

st.text_input(
    "Search by name",
    placeholder="Type a name...",
    key="search_query",
    disabled=st.session_state.user_selected
)

search_results = []

if st.session_state.search_query.strip() and not st.session_state.user_selected:
    try:
        response = requests.get(
            f"{BACKEND_URL}/search",
            params={"q": st.session_state.search_query, "limit": 10},
            timeout=5
        )
        if response.status_code == 200:
            search_results = response.json()["results"]
    except requests.RequestException:
        st.error("Backend not reachable")



if (
    st.session_state.search_query.strip()
    and search_results
    and not st.session_state.user_selected
):
    st.markdown("**Suggestions**")
    for user in search_results:
        if st.button(
            f"{user['first_name']} {user['last_name']}",
            key=f"search_{user['uid']}"
        ):
            st.session_state.target_user = user
            st.session_state.recommendations = []
            st.session_state.user_selected = True
            st.session_state.recommend_fetched = False



if st.session_state.target_user:
    user = st.session_state.target_user

    st.subheader("🎯 Selected User")
    st.image(user["profile_pic"], width=140)
    st.markdown(f"**{user['first_name']} {user['last_name']}**")
    st.write(f"Gender: {user['gender']}")
    st.write(f"Nationality: {user['nat']}")



if st.session_state.target_user and not st.session_state.recommend_fetched:
    try:
        response = requests.get(
            f"{BACKEND_URL}/recommend",
            params={"uid": st.session_state.target_user["uid"], "limit": 12},
            timeout=10
        )
        if response.status_code == 200:
            st.session_state.recommendations = response.json()["recommendations"]
            st.session_state.recommend_fetched = True
        else:
            st.error("Recommendation failed")
    except requests.RequestException:
        st.error("Backend not reachable")



if st.session_state.recommendations:
    st.subheader("🤝 Recommended Users")

    cols = st.columns(3)

    for i, rec in enumerate(st.session_state.recommendations):
        with cols[i % 3]:
            st.image(rec["profile_pic"], width=120)
            st.markdown(f"**{rec['first_name']} {rec['last_name']}**")



if st.session_state.target_user and st.session_state.recommendations:
    st.subheader("📍 Recommendation Map")

    target = st.session_state.target_user
    recs = st.session_state.recommendations

    m = folium.Map(
        location=[float(target["latitude"]), float(target["longitude"])],
        zoom_start=2
    )

    # Target marker
    folium.Marker(
        location=[float(target["latitude"]), float(target["longitude"])],
        popup="Target User",
        icon=folium.Icon(color="red", icon="user")
    ).add_to(m)

    # Recommended users
    for u in recs:
        folium.Marker(
            location=[float(u["latitude"]), float(u["longitude"])],
            popup=f"{u['first_name']} {u['last_name']}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st_folium(m, width=700, height=450)
