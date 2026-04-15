# --- UPDATED SUBMIT SCORE LOGIC ---
if page == "Submit Score":
    st.title("⛳ Record Round")
    with st.form("score_entry"):
        c1, c2 = st.columns(2)
        player = c1.text_input("Player Name")
        date_obj = c2.date_input("Round Date")
        clean_date = date_obj.strftime('%m/%d')

        def score_putt_grid(start, end):
            header_cols = st.columns(9)
            for i, hole in enumerate(range(start, end + 1)):
                header_cols[i].write(f"**H{hole}**")
            score_cols = st.columns(9)
            scores = [score_cols[i].number_input("", 1, 15, 4, key=f"s{hole}", label_visibility="collapsed") for i, hole in enumerate(range(start, end + 1))]
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
                
                # Create the data exactly as it should look in the sheet
                data_dict = {"Name": player, "Date": clean_date, "Gross": sum(all_scores), "Putts": sum(all_putts)}
                for i in range(1, 19):
                    data_dict[f"H{i}"] = all_scores[i-1]
                    data_dict[f"P{i}"] = all_putts[i-1]
                
                new_row_df = pd.DataFrame([data_dict])
                
                # CRITICAL: Read the sheet with NO CACHE (ttl=0) before updating
                current_df = conn.read(worksheet="Scores", ttl=0)
                updated_df = pd.concat([current_df, new_row_df], ignore_index=True)
                
                # Update the sheet
                conn.update(worksheet="Scores", data=updated_df)
                st.success("Round Posted to Google Sheets!")
                st.cache_data.clear() # Clears the cache for the leaderboard
            else:
                st.error("Please enter a Player Name.")
