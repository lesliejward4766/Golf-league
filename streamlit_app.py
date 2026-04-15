import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Establish the connection to your Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Add a way to clear the cache so the app doesn't "remember" old versions of your sheet
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
    
# Page Configuration
st.set_page_config(page_title="Golf League Hub", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# Sidebar Navigation
page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Score", "Master Leaderboard", "Commish Portal"])

# --- 1. TEE TIME SIGN-UP ---
if page == "Tee Time Sign-up":
    try:
        # Get the league date from the Settings tab
        settings_df = conn.read(worksheet="Settings", ttl=0)
        current_league_date = settings_df.iloc[0]['Value']
    except Exception:
        current_league_date = "Next Event"

    st.title(f"📅 Sign-up for {current_league_date}")
    
    try:
        # Read the current tee sheet
        df_times = conn.read(worksheet="TeeTimes", ttl=0)
        st.dataframe(df_times, use_container_width=True, hide_index=True)

        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Your Name")
            # Create list of times from the 'Time' column in your sheet
            time_options = df_times["Time"].tolist() if "Time" in df_times.columns else []
            selected_time = col2.selectbox("Select a Time Slot", time_options)
            submit_signup = st.form_submit_button("Join Group")

            if submit_signup and name:
                # Find the row for the selected time
                row_idx = df_times.index[df_times['Time'] == selected_time][0]
                added = False
                # Look for the first empty player slot
                for col in ["Player 1", "Player 2", "Player 3", "Player 4"]:
                    if col in df_times.columns:
                        if pd.isna(df_times.at[row_idx, col]) or str(df_times.at[row_idx, col]).strip() == "":
                            df_times.at[row_idx, col] = name
                            added = True
                            break
                
                if added:
                    conn.update(worksheet="TeeTimes", data=df_times)
                    st.success(f"Added {name} to {selected_time}!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("This tee time is full!")
    except Exception as e:
        st.error("⚠️ Tee sheet not found. Please ensure the 'TeeTimes' tab exists with headers: Time, Player 1, Player 2, Player 3, Player 4")

# --- 2. SUBMIT SCORE ---
elif page == "Submit Score":
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
            
            # Score Inputs (Collapsed label for clean look)
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
                
                data_dict = {
                    "Name": player, 
                    "Date": clean_date,
                    "Gross": sum(all_scores), 
                    "Putts": sum(all_putts)
                }
                # Map individual holes
                for i in range(1, 19):
                    data_dict[f"H{i}"] = all_scores[i-1]
                    data_dict[f"P{i}"] = all_putts[i-1]
                
                current = conn.read(worksheet="Scores")
                updated = pd.concat([current, pd.DataFrame([data_dict])], ignore_index=True)
                conn.update(worksheet="Scores", data=updated)
                
                st.success("Score Posted Successfully!")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Please enter a Player Name.")

# --- 3. MASTER LEADERBOARD ---
elif page == "Master Leaderboard":
    st.title("🏆 Leaderboard")
    try:
        df = conn.read(worksheet="Scores")
        if not df.empty:
            st.dataframe(df[['Date', 'Name', 'Gross', 'Putts']].sort_values("Date", ascending=False), use_container_width=True)
        else:
            st.info("No scores recorded yet.")
    except:
        st.error("Could not find 'Scores' tab in Google Sheets.")

# --- 4. COMMISH PORTAL ---
elif page == "Commish Portal":
    st.title("👨‍💼 Commissioner Tools")
    pwd = st.text_input("Enter Admin Password", type="password")
    
    if pwd == "golf2026":
        st.success("Admin access granted!")
        st.subheader("Weekly Management")
        new_date = st.text_input("Set Next League Date (e.g., 4/25)", value="4/25")
        
        if st.button("Update Date & Clear Tee Sheet"):
            try:
                # Update Settings Tab
                new_settings = pd.DataFrame([{"Setting": "LeagueDate", "Value": new_date}])
                conn.update(worksheet="Settings", data=new_settings)
                
                # Clear TeeTimes Tab
                df_times = conn.read(worksheet="TeeTimes")
                for col in ["Player 1", "Player 2", "Player 3", "Player 4"]:
                    if col in df_times.columns:
                        df_times[col] = ""
                conn.update(worksheet="TeeTimes", data=df_times)
                
                st.success(f"Sheet reset for {new_date}!")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Error during reset: {e}")
