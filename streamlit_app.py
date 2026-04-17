import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SETUP
st.set_page_config(page_title="Golf League Hub", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. NAVIGATION
page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Score", "Master Leaderboard", "Commish Portal"])

# --- 3. TEE TIME SIGN-UP ---
if page == "Tee Time Sign-up":
    try:
        settings_df = conn.read(worksheet="Settings", ttl=0)
        current_date = settings_df.iloc[0]['Value']
        st.title(f"📅 Sign-up: {current_date}")
        
        df_times = conn.read(worksheet="TeeTimes", ttl=0)
        st.dataframe(df_times, use_container_width=True, hide_index=True)

        with st.form("signup"):
            n = st.text_input("Name")
            t = st.selectbox("Time", df_times["Time"].tolist())
            if st.form_submit_button("Join Group"):
                if n:
                    row_idx = df_times.index[df_times['Time'] == t][0]
                    for col in ["Player 1", "Player 2", "Player 3", "Player 4"]:
                        if pd.isna(df_times.at[row_idx, col]) or str(df_times.at[row_idx, col]).strip() == "":
                            df_times.at[row_idx, col] = n
                            conn.update(worksheet="TeeTimes", data=df_times)
                            st.success(f"Added {n}!")
                            st.cache_data.clear()
                            st.rerun()
                            break
    except:
        st.error("Sheet Syncing... Check that 'TeeTimes' and 'Settings' tabs are ready.")

# --- 4. SUBMIT SCORE ---
elif page == "Submit Score":
    st.title("⛳ Record Round")
    with st.form("score_entry"):
        c1, c2 = st.columns(2)
        player = c1.text_input("Player Name")
        date_obj = c2.date_input("Round Date")
        
        def score_putt_grid(start):
            h_cols = st.columns(9)
            s_list, p_list = [], []
            for i in range(9):
                with h_cols[i]:
                    hole = start + i
                    st.write(f"**H{hole}**")
                    s = st.number_input("S", 1, 15, 4, key=f"s_{hole}", label_visibility="collapsed")
                    p = st.number_input("P", 0, 5, 2, key=f"p_{hole}")
                    s_list.append(s)
                    p_list.append(p)
            return s_list, p_list

        f_s, f_p = score_putt_grid(1)
        st.write("---")
        b_s, b_p = score_putt_grid(10)

        if st.form_submit_button("Post Score"):
            if player:
                all_s, all_p = f_s + b_s, f_p + b_p
                data = {"Name": player, "Date": date_obj.strftime('%m/%d'), "Gross": sum(all_s), "Putts": sum(all_p)}
                for i in range(1, 19):
                    data[f"H{i}"], data[f"P{i}"] = all_s[i-1], all_p[i-1]
                
                current = conn.read(worksheet="Scores", ttl=0)
                updated = pd.concat([current, pd.DataFrame([data])], ignore_index=True)
                conn.update(worksheet="Scores", data=updated)
                st.success("Score Saved!")
                st.balloons()
                st.cache_data.clear()

# --- 5. MASTER LEADERBOARD ---
elif page == "Master Leaderboard":
    st.title("🏆 Leaderboard")
    try:
        df = conn.read(worksheet="Scores", ttl=0)
        st.dataframe(df[['Date', 'Name', 'Gross', 'Putts']].sort_values("Date", ascending=False))
    except:
        st.info("No scores yet.")

# --- 6. COMMISH PORTAL ---
elif page == "Commish Portal":
    st.title("👨‍💼 Admin")
    if st.text_input("Password", type="password") == "golf2026":
        d = st.text_input("Next Date", value="4/25")
        if st.button("Reset Week"):
            conn.update(worksheet="Settings", data=pd.DataFrame([{"Setting": "LeagueDate", "Value": d}]))
            df_t = conn.read(worksheet="TeeTimes", ttl=0)
            for c in ["Player 1", "Player 2", "Player 3", "Player 4"]: df_t[c] = ""
            conn.update(worksheet="TeeTimes", data=df_t)
            st.success("Reset successful!")
            st.cache_data.clear()
