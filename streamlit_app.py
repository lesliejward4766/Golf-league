import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SETUP & CONNECTION
st.set_page_config(page_title="Golf League Hub", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. SIDEBAR NAVIGATION
# This MUST come before the "if page ==" logic
page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Score", "Master Leaderboard", "Commish Portal"])

# 3. TEE TIME SIGN-UP
if page == "Tee Time Sign-up":
    try:
        settings_df = conn.read(worksheet="Settings", ttl=0)
        current_league_date = settings_df.iloc[0]['Value']
    except:
        current_league_date = "Next Event"

    st.title(f"📅 Sign-up for {current_league_date}")
    
    try:
        df_times = conn.read(worksheet="TeeTimes", ttl=0)
        st.dataframe(df_times, use_container_width=True, hide_index=True)

        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Your Name")
            time_list = df_times["Time"].tolist() if "Time" in df_times.columns else []
            selected_time = col2.selectbox("Select a Time Slot", time_list)
            
            if st.form_submit_button("Join Group"):
                if name:
                    row_idx = df_times.index[df_times['Time'] == selected_time][0]
                    added = False
                    for col in ["Player 1", "Player 2", "Player 3", "Player 4"]:
                        if pd.isna(df_times.at[row_idx, col]) or str(df_times.at[row_idx, col]).strip() == "":
                            df_times.at[row_idx, col] = name
                            added = True
                            break
                    if added:
                        conn.update(worksheet="TeeTimes", data=df_times)
                        st.success(f"Added {name}!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Time slot full!")
    except:
        st.error("Check 'TeeTimes' tab in Google Sheets.")

# 4. SUBMIT SCORE
elif page == "Submit Score":
    st.title("⛳ Record Round")
    with st.form("score_entry"):
        c1, c2 = st.columns(2)
        player = c1.text_input("Player Name")
        date_obj = c2.date_input("Round Date")
        
        st.write("---")
        def score_putt_grid(start, end):
            h_cols = st.columns(9)
            for i, hole in enumerate(range(start, end + 1)):
                h_cols[i].write(f"**H{hole}**")
            s_cols = st.columns(9)
            scores = [s_cols[i].number_input("", 1, 15, 4, key=f"s{hole}", label_visibility="collapsed") for i in range(9)]
            p_cols = st.columns(9)
            putts = [p_cols[i].number_input("P", 0, 5, 2, key=f"p{hole}") for i in range(9)]
            return scores, putts

        f_scores, f_putts = score_putt_grid(1, 9)
        st.write("---")
        b_scores, b_putts = score_putt_grid(10, 18)

        if st.form_submit_button("Post Score"):
            if player:
                # Combine all data into one row
                all_s = f_scores + b_scores
                all_p = f_putts + b_putts
                data = {"Name": player, "Date": date_obj.strftime('%m/%d'), "Gross": sum(all_s), "Putts": sum(all_p)}
                for i in range(1, 19):
                    data[f"H{i}"] = all_s[i-1]
                    data[f"P{i}"] = all_p[i-1]
                
                # Update Sheet
                current_df = conn.read(worksheet="Scores", ttl=0)
                updated_df = pd.concat([current_df, pd.DataFrame([data])], ignore_index=True)
                conn.update(worksheet="Scores", data=updated_df)
                st.success("Round Recorded!")
                st.cache_data.clear()

# 5. MASTER LEADERBOARD
elif page == "Master Leaderboard":
    st.title("🏆 Leaderboard")
    try:
        df = conn.read(worksheet="Scores", ttl=0)
        if not df.empty:
            st.dataframe(df[['Date', 'Name', 'Gross', 'Putts']].sort_values("Date", ascending=False))
    except:
        st.info("No scores yet.")

# 6. COMMISH PORTAL
elif page == "Commish Portal":
    st.title("👨‍💼 Admin")
    if st.text_input("Password", type="password") == "golf2026":
        new_date = st.text_input("Next Date", value="4/18")
        if st.button("Reset Week"):
            # Update Date
            conn.update(worksheet="Settings", data=pd.DataFrame([{"Setting": "LeagueDate", "Value": new_date}]))
            # Clear Tee Times
            df_t = conn.read(worksheet="TeeTimes", ttl=0)
            for c in ["Player 1", "Player 2", "Player 3", "Player 4"]: df_t[c] = ""
            conn.update(worksheet="TeeTimes", data=df_t)
            st.success("Weekly reset complete!")
            st.cache_data.clear()
