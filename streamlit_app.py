import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Golf League Hub", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Score", "Master Leaderboard", "Stats", "Commish Portal"])

# --- 1. SUBMIT SCORE ---
if page == "Submit Score":
    st.title("⛳ Record Round")
    with st.form("score_entry"):
        c1, c2, c3 = st.columns(3)
        player = c1.selectbox("Player", ["Arnold", "Baker", "Botla", "Brenner"]) # Add your full roster here
        flight = c2.selectbox("Flight", ["A", "B", "C"])
        date = c3.date_input("Round Date")
        
        game_points = c1.number_input("Game/Points", value=0.0)
        
        st.write("---")
        st.subheader("Scores (Hole-by-Hole)")
        
        # Grid for score entry
        f_cols = st.columns(9)
        f_scores = [f_cols[i].number_input(f"{i+1}", 1, 15, 4, key=f"f{i}") for i in range(9)]
        
        b_cols = st.columns(9)
        b_scores = [b_cols[i].number_input(f"{i+10}", 1, 15, 4, key=f"b{i}") for i in range(9)]
        
        st.write("---")
        putts = st.number_input("Total Putts (Optional)", value=0)

        if st.form_submit_button("Post to Master"):
            gross = sum(f_scores) + sum(b_scores)
            new_data = pd.DataFrame([{
                "Name": player, "Flight": flight, "Date": str(date), 
                "Gross": gross, "Game": game_points, "Putts": putts
            }])
            
            current = conn.read(worksheet="Scores")
            updated = pd.concat([current, new_data], ignore_index=True)
            conn.update(worksheet="Scores", data=updated)
            st.success(f"Successfully posted {gross} for {player}!")
            st.cache_data.clear()

# --- 2. MASTER LEADERBOARD (The "Clip" View) ---
elif page == "Master Leaderboard":
    st.title("🏆 Season Master Sheet")
    df = conn.read(worksheet="Scores")
    
    if not df.empty:
        # This "pivots" the data to look like your screenshot
        master_view = df.pivot_table(
            index=['Name', 'Flight'], 
            columns='Date', 
            values=['Gross', 'Game'], 
            aggfunc='first'
        ).fillna('-')
        
        st.dataframe(master_view, use_container_width=True)

# --- 3. TEE TIME SIGN-UP ---
elif page == "Tee Time Sign-up":
    st.title("📅 Weekly Tee Times")
    df_times = conn.read(worksheet="TeeTimes")
    st.dataframe(df_times, use_container_width=True)
    with st.form("signup"):
        n = st.text_input("Name")
        t = st.selectbox("Time", ["8:00", "8:10", "8:20", "8:30"])
        if st.form_submit_button("Sign Up"):
            new_t = pd.DataFrame([{"Name": n, "Time": t, "Date": "Saturday"}])
            conn.update(worksheet="TeeTimes", data=pd.concat([df_times, new_t], ignore_index=True))
            st.cache_data.clear()
            st.rerun()

# --- 4. COMMISH PORTAL ---
elif page == "Commish Portal":
    st.title("👨‍💼 Commissioner Tools")
    if st.text_input("Password", type="password") == "golf2026":
        st.write("Logged in as Commish.")
        if st.button("Reset Tee Times"):
            conn.update(worksheet="TeeTimes", data=pd.DataFrame(columns=["Name", "Time", "Date"]))
            st.success("Tee times cleared.")
