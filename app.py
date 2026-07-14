import streamlit as st
import pandas as pd

# Page setup for mobile responsiveness
st.set_page_config(page_title="Accessories Tracker", layout="centered")

st.title("📱 Engineer Accessories Tracker")

# ⚠️ အဆင့် (၁) က ရလာတဲ့ သင်၏ Google Sheet CSV Link ကို အောက်ကနေရာမှာ အစားထိုးပါ
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60) # ၁ မိနစ်ပြည့်တိုင်း Data အသစ်ကို Sheet ထဲကနေ Auto ဆွဲယူမည်
def load_data():
    df = pd.read_csv(GSHEET_CSV_URL)
    return df

try:
    df = load_data()
    
    # ပြသလိုသော Column များ
    display_cols = [
        'Date', 'Engineer Name', 'Patch Cords(SC/APC) 1M', 
        'Patch Cords(SC/APC) 1.5M', 'One Core OTB Box', 'Sleeve', 
        'Customize (Pencil Kit , white)', 'Standard (Pencil Kit , white)'
    ]
    
    # Sheet ထဲမှာ ရှိတဲ့ column တွေနဲ့ တိုက်စစ်ခြင်း
    available_cols = [col for col in display_cols if col in df.columns]
    filtered_df = df[available_cols].copy()

    # Dropdown အတွက် Engineer Name များ ထုတ်ယူခြင်း
    engineers = sorted(filtered_df['Engineer Name'].dropna().unique())
    
    # Dropdown UI
    selected_engineer = st.selectbox(
        "👷 Select Engineer Name:",
        options=["All Engineers"] + list(engineers)
    )
    
    st.divider()

    # Filter Logic
    if selected_engineer != "All Engineers":
        result_df = filtered_df[filtered_df['Engineer Name'] == selected_engineer]
    else:
        result_df = filtered_df

    # ဇယားဖြင့် ပြသခြင်း
    if not result_df.empty:
        st.subheader(f"📊 {selected_engineer} စာရင်း")
        st.dataframe(result_df, use_container_width=True, hide_index=True)
        
        # ကိန်းဂဏန်းများ စုစုပေါင်းကို တွက်ပြရန်
        st.subheader("📈 Total Used Summary")
        numeric_cols = result_df.select_dtypes(include='number').columns
        if not numeric_cols.empty:
            summary_data = result_df[numeric_cols].sum().reset_index()
            summary_data.columns = ['ပစ္စည်းအမျိုးအမည်', 'စုစုပေါင်းအရေအတွက်']
            st.table(summary_data)
    else:
        st.warning("ဒေတာ မရှိသေးပါ။")

except Exception as e:
    st.error(f"Data ချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")
