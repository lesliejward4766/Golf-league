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
    st.write("Enter your score and putts (P) for each hole.")
    
    with st.form("score_entry"):
        c1, c2 = st.columns(2)
        player = c1.text_input("Player Name")
        date_obj = c2.date_input("Round Date")
        clean_date = date_obj.strftime('%m/%d')

        st.write("---")
        
        def score_putt_grid(start, end):
            # Header Row
            header_cols = st.columns(9)
            for i, hole in enumerate(range(start, end + 1)):
                header_cols[i].write(f"**H{hole}**")
            
            # Score Inputs (No label)
            score_cols = st.columns(9)
            scores = [score_cols[i].number_input("", 1, 15, 4, key=f"s{hole}", label_visibility="collapsed") for i, hole in enumerate(range(start, end + 1))]
            
            # Putt Inputs (Labeled 'P')
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
                
                data_dict = {
                    "Name": player, 
                    "Date": clean_date,
                    "Gross": gross, 
                    "Putts": total_putts
                }
                
                # Mapping individual hole data
                for i in range(1, 19):
                    data_dict[f"H{i}"] = all_scores[i-1]
                    data_dict[f"P{i}"] = all_putts[i-1]
                
                new_data = pd.DataFrame([data_dict])
                
                # Write to Google Sheet
                current = conn.read(worksheet="Scores")
                updated = pd.concat([current, new_data], ignore_index=True)
                conn.update(worksheet="Scores", data=updated)
                
                st.success(f"Posted! Gross: {gross} | Putts: {total_putts}")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Please enter a Name.")

# --- 2. MASTER LEADERBOARD ---
elif page == "Master Leaderboard":
    st.title("🏆 Leaderboard")
    df = conn.read(worksheet="Scores")
    if not df.empty:
        st.dataframe(df[['Date', 'Name', 'Gross', 'Putts']].sort_values("Date", ascending=False), use_container_width=True)

# --- 3. TEE TIME SIGN-UP ---
elif page == "Tee Time Sign-up":
    # Pull the current sheet
    df_times = conn.read(worksheet="TeeTimes", ttl=0)
    
    # We'll use a specific cell in your sheet (or a Streamlit secret) to store the 'Current Date'
    # For now, let's assume the first row of a new "Settings" tab has the date
    try:
        settings_df = conn.read(worksheet="Settings")
        current_league_date = settings_df.iloc[0]['Value']
    except:
        current_league_date = "Next Event"

    st.title(f"📅 Sign-up for {current_league_date}")
    st.write("Find an open slot and add your name.")
    
    st.dataframe(df_times, use_container_width=True, hide_index=True)

    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Your Name")
        selected_time = col2.selectbox("Select a Time Slot", df_times["Time"].tolist())
        submit_signup = st.form_submit_button("Join Group")

        if submit_signup and name:
            row_idx = df_times.index[df_times['Time'] == selected_time][0]
            added = False
            for col in ["Player 1", "Player 2", "Player 3", "Player 4"]:
                if pd.isna(df_times.at[row_idx, col]) or df_times.at[row_idx, col] == "":
                    df_times.at[row_idx, col] = name
                    added = True
                    break
            
            if added:
                conn.update(worksheet="TeeTimes", data=df_times)
                st.success(f"Added to {selected_time}!")
                st.cache_data.clear()
                st.rerun()

# --- 4. COMMISH ---
elif page == "Commish Portal":
    st.title("👨‍💼 Admin")
    if st.text_input("Password", type="password") == "golf2026":
        st.write("Commish Access Active.")
