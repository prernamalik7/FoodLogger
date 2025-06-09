import streamlit as st
import pandas as pd
from datetime import date
import re

# Load calorie data
calorie_db = pd.read_csv("calories.csv")

# User input
st.title("Free AI-Like Calorie Tracker")
food_input = st.text_area("What did you eat today?")
entry_date = st.date_input("Entry Date", value=date.today())

def parse_foods(input_text):
    food_log = []
    text = input_text.lower()
    for _, row in calorie_db.iterrows():
        # Regex pattern:
        # looks for a number + optional unit + food (like "2 cups rice")
        pattern = rf"(\d+)\s*(cup|cups|piece|pieces|slice|slices|tablespoon|tablespoons|grams|gram|g)?\s*{re.escape(row['food'])}"
        match = re.search(pattern, text)
        if match:
            quantity = int(match.group(1))
        else:
            # fallback: if food word exists but no number found, assume 1
            if row['food'] in text:
                quantity = 1
            else:
                continue

        total_cal = quantity * row['calories']
        food_log.append((row['food'], quantity, row['unit'], total_cal))
    return food_log

if st.button("Log"):
    parsed = parse_foods(food_input)
    total = sum([item[3] for item in parsed])

    # Show results
    st.subheader(f"Total Calories: {total}")
    df_entry = pd.DataFrame(parsed, columns=["Food", "Quantity", "Unit", "Calories"])
    st.dataframe(df_entry)

    # Save to CSV
    log_df = pd.DataFrame([[entry_date, total]], columns=["Date", "Calories"])
    try:
        existing = pd.read_csv("log.csv")
        combined = pd.concat([existing, log_df])
    except FileNotFoundError:
        combined = log_df
    combined.to_csv("log.csv", index=False)

# View calendar
if st.checkbox("Show Calorie Chart"):
    try:
        logs = pd.read_csv("log.csv")
        logs['Date'] = pd.to_datetime(logs['Date'])
        chart = logs.groupby('Date')['Calories'].sum()
        st.line_chart(chart)
    except FileNotFoundError:
        st.warning("No logs yet.")
