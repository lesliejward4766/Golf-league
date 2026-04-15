import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Golf League Hub", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

page = st.sidebar.radio("Go To:", ["Tee Time Sign-up", "Submit Score", "Master Leaderboard", "Commish Portal"])

# --- 1. SUBMIT SCORE ---
if page == "Submit Score":
    st.title("⛳ Record Round")
    st.write("Enter your scores and putts for all 18 holes.")
    
    with st.form("score_entry"):
        c1, c2 = st.columns(2)
        player = c1.text_input("Player Name")
        date = c2.date_input("Round Date")
        flight = c1.selectbox("Flight", ["A", "B", "C", "D"])

        st.write("---")
        
        # Helper function to create the 9-hole entry grid
        def score_putt_grid(start, end):
            # Create a row of headers
            header_cols = st.columns(9)
            for i, hole in enumerate(range(start, end + 1)):
                header_cols[i].write(f"**H{hole}**")
            
            # Create a row for Scores
            score_cols = st.columns(9)
            scores = [score_cols[i].number_input("Score", 1, 15, 4, key=f"s{hole}", label_visibility="collapsed") for i, hole in enumerate(range(start, end + 1))]
            
            # Create a row for Putts
            putt_cols = st.columns(9)
            putts = [putt_cols[i].number_input("Putts", 0, 5, 2, key=f"p{hole}", label_visibility="collapsed") for i, hole in enumerate(range(start, end + 1))]
            
            return scores, putts

        st.subheader("Front 9 (Top: Score | Bottom: Putts)")
        f_scores, f_putts = score_putt_grid(1, 9)
        
        st.write("---")
        
        st.subheader("Back 9 (Top: Score | Bottom: Putts)")
        b_scores, b_putts = score_putt_grid(10, 18)

        if st.form_submit_button("Post to Master"):
            if player:
                all_scores = f_scores + b_scores
                all_putts = f_putts + b_putts
                
                gross = sum(all_scores)
                total_putts = sum(all_putts)
                
                # Matching your vertical database needs
                new_data = pd.DataFrame([{
                    "Name": player, 
                    "Flight": flight, 
                    "Date": date.strftime('%m/%d/%y'),
                    "Gross": gross, 
                    "Putts": total_putts,
                    **{f"H{i+1}": s for i, s in enumerate(all_scores)}, # Individual scores
                    **{f"P{i+1}": p for i, p in enumerate(all_putts)}   # Individual putts
                }])
                
                current = conn.read(worksheet="Scores")
                updated = pd.concat([current, new_data], ignore_index=True)
                conn.update(worksheet="Scores", data=updated)
                
                st.success(f"Successfully posted! Gross: {gross} | Putts: {total_putts}")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Please enter a Player Name.")

# --- KEEP OTHER PAGES FOR TESTING ---
elif page == "Master Leaderboard":
    st.title("🏆 Season Master Sheet")
    df = conn.read(worksheet="Scores")
    if not df.empty:
        st.dataframe(df[['Date', 'Name', 'Gross', 'Putts']].sort_values("Date"), use_container_width=True)

elif page == "Tee Time Sign-up":
    st.title("📅 Weekly Tee Times")
    df_times = conn.read(worksheet="TeeTimes")
    st.dataframe(df_times, use_container_width=True)

elif page == "Commish Portal":
    st.title("👨‍💼 Admin")
    if st.text_input("Password", type="password") == "golf2026":
        st.write("Admin access granted.")
