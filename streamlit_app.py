import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Set up page
st.set_page_config(page_title="Golf League Hub", layout="centered")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- APP NAVIGATION ---
page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Scorecard", "Leaderboard", "Commish Portal"])

# --- 1. TEE TIME SIGN-UP ---
if page == "Tee Time Sign-up":
    st.title("📅 Weekly Sign-up")
    
    # Read existing sign-ups
    df = conn.read(worksheet="TeeTimes")
    
    st.write("Current Roster for Saturday:")
    st.dataframe(df, use_container_width=True)

    with st.form("signup"):
        name = st.text_input("Your Name")
        time = st.selectbox("Select Time", ["8:00", "8:10", "8:20", "8:30"])
        submit = st.form_submit_button("Join Group")
        
        if submit and name:
            new_data = pd.DataFrame([{"Name": name, "Time": time, "Date": "Saturday"}])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="TeeTimes", data=updated_df)
            st.success("You're in! Refresh to see your name.")
            st.cache_data.clear()

# --- 2. SUBMIT SCORECARD ---
elif page == "Submit Scorecard":
    st.title("📸 Scorecard Upload")
    player = st.text_input("Player Name")
    photo = st.file_uploader("Take a photo of the scorecard", type=['png', 'jpg', 'jpeg'])
    
    if photo and player:
        if st.button("Submit to Commissioner"):
            # This temporarily stores the photo in Streamlit's memory 
            # In a free app, we'll display these in the Commish Portal
            st.session_state[f"photo_{player}"] = photo
            st.success("Uploaded! The Commish will review this shortly.")

# --- 3. LEADERBOARD ---
elif page == "Leaderboard":
    st.title("🏆 League Standings")
    scores_df = conn.read(worksheet="Scores")
    st.table(scores_df.sort_values(by="GrossScore"))

# --- 4. COMMISH PORTAL (Admin Only) ---
elif page == "Commish Portal":
    st.title("👨‍💼 Commissioner Tools")
    pwd = st.text_input("Enter Admin Password", type="password")
    
    if pwd == "golf2026": # Change this to your desired password
        st.header("Pending Scorecards")
        # This displays any photos uploaded during the current session
        for key in st.session_state.keys():
            if key.startswith("photo_"):
                st.write(f"Upload from: {key.replace('photo_', '')}")
                st.image(st.session_state[key])
                
        st.header("Update Scores")
        with st.form("update_scores"):
            p_name = st.text_input("Player Name")
            p_score = st.number_input("Gross Score", min_value=60, max_value=150)
            update_btn = st.form_submit_button("Post Score")
            
            if update_btn:
                score_data = conn.read(worksheet="Scores")
                new_score = pd.DataFrame([{"Player": p_name, "GrossScore": p_score}])
                final_scores = pd.concat([score_data, new_score], ignore_index=True)
                conn.update(worksheet="Scores", data=final_scores)
                st.success("Score posted to the leaderboard!")
                st.cache_data.clear()
