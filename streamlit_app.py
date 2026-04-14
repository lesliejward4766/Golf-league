import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page Config
st.set_page_config(page_title="Golf League Hub", layout="centered")
conn = st.connection("gsheets", type=GSheetsConnection)

# Sidebar Navigation
page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Scorecard", "Leaderboard", "Stats", "Commish Portal"])

# --- 1. TEE TIME SIGN-UP ---
if page == "Tee Time Sign-up":
    st.title("📅 Weekly Sign-up")
    df_times = conn.read(worksheet="TeeTimes")
    st.write("Current Sign-ups:")
    st.dataframe(df_times, use_container_width=True)

    with st.form("signup"):
        name = st.text_input("Your Name")
        time = st.selectbox("Select Time", ["8:00", "8:10", "8:20", "8:30", "8:40", "8:50"])
        submit = st.form_submit_button("Join Group")
        
        if submit and name:
            new_entry = pd.DataFrame([{"Name": name, "Time": time, "Date": "Saturday"}])
            updated_df = pd.concat([df_times, new_entry], ignore_index=True)
            conn.update(worksheet="TeeTimes", data=updated_df)
            st.success("You're signed up! Refresh to see the list.")
            st.cache_data.clear()

# --- 2. SUBMIT SCORECARD ---
elif page == "Submit Scorecard":
    st.title("⛳ Hole-by-Hole Entry")
    with st.form("score_entry"):
        col_a, col_b = st.columns(2)
        player = col_a.text_input("Player Name")
        hcp = col_b.number_input("Course Handicap", min_value=0, max_value=54, value=0)
        date = st.date_input("Round Date")
        
        st.write("---")
        st.write("**Front 9**")
        f_cols = st.columns(9)
        h1 = f_cols[0].number_input("1", 1, 15, 4)
        h2 = f_cols[1].number_input("2", 1, 15, 4)
        h3 = f_cols[2].number_input("3", 1, 15, 4)
        h4 = f_cols[3].number_input("4", 1, 15, 4)
        h5 = f_cols[4].number_input("5", 1, 15, 4)
        h6 = f_cols[5].number_input("6", 1, 15, 4)
        h7 = f_cols[6].number_input("7", 1, 15, 4)
        h8 = f_cols[7].number_input("8", 1, 15, 4)
        h9 = f_cols[8].number_input("9", 1, 15, 4)

        st.write("**Back 9**")
        b_cols = st.columns(9)
        h10 = b_cols[0].number_input("10", 1, 15, 4)
        h11 = b_cols[1].number_input("11", 1, 15, 4)
        h12 = b_cols[2].number_input("12", 1, 15, 4)
        h13 = b_cols[3].number_input("13", 1, 15, 4)
        h14 = b_cols[4].number_input("14", 1, 15, 4)
        h15 = b_cols[5].number_input("15", 1, 15, 4)
        h16 = b_cols[6].number_input("16", 1, 15, 4)
        h17 = b_cols[7].number_input("17", 1, 15, 4)
        h18 = b_cols[8].number_input("18", 1, 15, 4)

        if st.form_submit_button("Submit Round"):
            if player:
                scores = [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18]
                gross = sum(scores)
                net = gross - hcp
                new_row = pd.DataFrame([{
                    "Player": player, "Date": str(date), "Gross": gross, "Handicap": hcp, "Net": net,
                    "H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5, "H6": h6, "H7": h7, "H8": h8, "H9": h9,
                    "H10": h10, "H11": h11, "H12": h12, "H13": h13, "H14": h14, "H15": h15, "H16": h16, "H17": h17, "H18": h18
                }])
                current = conn.read(worksheet="Scores")
                updated = pd.concat([current, new_row], ignore_index=True)
                conn.update(worksheet="Scores", data=updated)
