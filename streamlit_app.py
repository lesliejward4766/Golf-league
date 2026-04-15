import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Golf League Hub", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# Navigation
page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Score", "Master Leaderboard", "Commish Portal"])

# --- 1. SUBMIT SCORE ---
if page == "Submit Score":
    st.title("⛳ Record Round")
    with st.form("score_entry"):
        c1, c2, c3 = st.columns(3)
        player = c1.text_input("Player Name")
        flight = c2.selectbox("Flight", ["A", "B", "C", "D"])
        date = c3.date_input("Round Date")
        
        game_points = c1.number_input("Game/Points", value=0.0, step=0.5)
        
        st.write("---")
        st.subheader("Scores (Hole-by-Hole)")
        
        # Grid for score entry (Front 9)
        st.write("**Front 9**")
        f_cols = st.columns(9)
        f_scores = [f_cols[i].number_input(f"{i+1}", 1, 15, 4, key=f"f{i}") for i in range(9)]
        
        # Grid for score entry (Back 9)
        st.write("**Back 9**")
        b_cols = st.columns(9)
        b_scores = [b_cols[i].number_input(f"{i+10}", 1, 15, 4, key=f"b{i}") for i in range(9)]
        
        st.write("---")
        putts = st.number_input("Total Putts (Optional)", value=0)

        if st.form_submit_button("Post to Master"):
            if player:
                gross = sum(f_scores) + sum(b_scores)
                new_data = pd.DataFrame([{
                    "Name": player, 
                    "Flight": flight, 
                    "Date": date.strftime('%m/%d/%y'), # Formats date like your clip
                    "Gross": gross, 
                    "Game": game_points, 
                    "Putts": putts
                }])
                
                # Pull existing data and append
                current = conn.read(worksheet="Scores")
                updated = pd.concat([current, new_data], ignore_index=True)
                conn.update(worksheet="Scores", data=updated)
                
                st.success(f"Successfully posted {gross} for {player}!")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Please enter a Player Name.")

# --- 2. MASTER LEADERBOARD (The "Clip" View) ---
elif page == "Master Leaderboard":
    st.title("🏆 Season Master Sheet")
    df = conn.read(worksheet="Scores")
    
    if not df.empty:
        # Pivot the data to match your screenshot layout
        # Dates across the top, Players/Flights on the left
        master_view = df.pivot_table(
            index=['Flight', 'Name'], 
            columns='Date', 
            values=['Gross', 'Game'], 
            aggfunc='first'
        ).fillna('-')
        
        # Display the pivoted table
        st.dataframe(master_view, use_container_width=True)
    else:
        st.info("No scores recorded yet. Go to 'Submit Score' to start your 2026 season!")

# --- 3. TEE TIME SIGN-UP ---
elif page == "Tee Time Sign-up":
    st.title("📅 Weekly Tee Times")
    df_times = conn.read(worksheet="TeeTimes")
    st.write("Add your name to a slot below:")
    st.dataframe(df_times, use_container_width=True)
    
    with st.form("signup"):
        n = st.text_input("Your Name")
        t = st.selectbox("Select Time", ["8:00", "8:10", "8:20", "8:30", "8:40", "8:50"])
        if st.form_submit_button("Sign Up"):
            if n:
                new_t = pd.DataFrame([{"Name": n, "Time": t, "Date": "Next Saturday"}])
                updated_t = pd.concat([df_times, new_t], ignore_index=True)
                conn.update(worksheet="TeeTimes", data=updated_t)
                st.success(f"Added {n} to the {t} slot.")
                st.cache_data.clear()
                st.rerun()

# --- 4. COMMISH PORTAL ---
elif page == "Commish Portal":
    st.title("👨‍💼 Commissioner Tools")
    pwd = st.text_input("Admin Password", type="password")
    
    if pwd == "golf2026":
        st.subheader("Data Management")
        if st.button("Reset Tee Times for New Week"):
            empty_df = pd.DataFrame(columns=["Name", "Time", "Date"])
            conn.update(worksheet="TeeTimes", data=empty_df)
            st.success("Tee times have been cleared.")
            st.cache_data.clear()
            
        st.write("---")
        st.write("View/Edit raw Scores tab in your Google Sheet for corrections.")
