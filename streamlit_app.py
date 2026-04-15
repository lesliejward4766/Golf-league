import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page Configuration for a mobile-friendly wide layout
st.set_page_config(page_title="Golf League Hub", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# Navigation
page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Score", "Master Leaderboard", "Commish Portal"])

# --- 1. SUBMIT SCORE ---
if page == "Submit Score":
    st.title("⛳ Record Round")
    st.write("Please enter your score and total putts for each hole.")
    
    with st.form("score_entry"):
        c1, c2 = st.columns(2)
        player = c1.text_input("Player Name")
        # Format date as Month/Day for the entry
        date_obj = c2.date_input("Round Date")
        clean_date = date_obj.strftime('%m/%d')

        st.write("---")
        
        # Helper function to create the scorecard grid
        def score_putt_grid(start, end):
            # Headers
            header_cols = st.columns(9)
            for i, hole in enumerate(range(start, end + 1)):
                header_cols[i].write(f"**H{hole}**")
            
            # Score Inputs
            score_cols = st.columns(9)
            scores = [score_cols[i].number_input("S", 1, 15, 4, key=f"s{hole}", label_visibility="visible") for i, hole in enumerate(range(start, end + 1))]
            
            # Putt Inputs
            putt_cols = st.columns(9)
            putts = [putt_cols[i].number_input("P", 0, 5, 2, key=f"p{hole}", label_visibility="visible") for i, hole in enumerate(range(start, end + 1))]
            
            return scores, putts

        st.subheader("Front 9")
        f_scores, f_putts = score_putt_grid(1, 9)
        
        st.write("---")
        
        st.subheader("Back 9")
        b_scores, b_putts = score_putt_grid(10, 18)

        if st.form_submit_button("Submit Round"):
            if player:
                all_scores = f_scores + b_scores
                all_putts = f_putts + b_putts
                
                gross = sum(all_scores)
                total_putts = sum(all_putts)
                
                # Create dictionary for the row
                data_dict = {
                    "Name": player, 
                    "Date": clean_date,
                    "Gross": gross, 
                    "Putts": total_putts
                }
                
                # Map individual hole data
                for i in range(1, 19):
                    data_dict[f"H{i}"] = all_scores[i-1]
                    data_dict[f"P{i}"] = all_putts[i-1]
                
                new_data = pd.DataFrame([data_dict])
                
                # Write to Google Sheet
                current = conn.read(worksheet="Scores")
                updated = pd.concat([current, new_data], ignore_index=True)
                conn.update(worksheet="Scores", data=updated)
                
                st.success(f"Successfully posted! Gross: {gross} | Putts: {total_putts}")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Please enter a Player Name to submit.")

# --- 2. MASTER LEADERBOARD ---
elif page == "Master Leaderboard":
    st.title("🏆 Leaderboard")
    df = conn.read(worksheet="Scores")
    if not df.empty:
        # Show simple summary sorted by latest date
        st.dataframe(df[['Date', 'Name', 'Gross', 'Putts']].sort_values("Date", ascending=False), use_container_width=True)
    else:
        st.info("No scores found. Start by submitting a round!")

# --- 3. TEE TIMES ---
elif page == "Tee Time Sign-up":
    st.title("📅 Weekly Tee Times")
    df_times = conn.read(worksheet="TeeTimes")
    st.dataframe(df_times, use_container_width=True)

# --- 4. COMMISH ---
elif page == "Commish Portal":
    st.title("👨‍💼 Admin")
    if st.text_input("Password", type="password") == "golf2026":
        st.write("Admin access granted.")
