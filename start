import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Golf League App", layout="centered")

# Connect to your Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("⛳ My Golf League Hub")

# --- TAB 1: TEE TIMES ---
tab1, tab2 = st.tabs(["📅 Tee Time Sign-up", "📸 Upload Scorecard"])

with tab1:
    st.header("Weekly Sign-up")
    # In a real app, you'd pull these from the sheet. 
    # For now, let's let players just type their entry.
    with st.form("tee_time_form"):
        name = st.text_input("Your Name")
        time_slot = st.selectbox("Preferred Time", ["8:00 AM", "8:10 AM", "8:20 AM", "8:30 AM"])
        submit_time = st.form_submit_button("Reserve Spot")
        
        if submit_time:
            st.success(f"Got it, {name}! You're down for {time_slot}.")
            # This is where we would append to the Google Sheet

# --- TAB 2: SCORECARD UPLOAD ---
with tab2:
    st.header("Submit Results")
    st.write("Take a photo of your scorecard below.")
    
    player_name = st.text_input("Player Name(s)")
    score_photo = st.file_uploader("Upload Scorecard", type=['jpg', 'jpeg', 'png'])
    
    if score_photo is not None:
        st.image(score_photo, caption="Preview", use_container_width=True)
        if st.button("Confirm Submission"):
            st.balloons()
            st.success("Scorecard sent to the Commish!")
