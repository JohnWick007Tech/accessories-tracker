import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics

# Page Configuration
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

with streamlit_analytics.track():

    st.markdown("<h3 style='text-align: center;'>📱 Eng Usage Checker</h3>", unsafe_allow_html=True)

    # ⚠️ Google Sheet URLs
    BASE_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc"
    
    # ၁။ EngUsageTracker တဘ် (gid=0)
    USAGE_CSV_URL = f"{BASE_URL}/export?format=csv&gid=0"
    
    # ၂။ Out တဘ် (ထည့်သွင်းပေးထားသော gid ဖြစ်ပါသည်)
    OUT_CSV_URL = f"{BASE_URL}/export?format=csv&gid=147444867"

    @st.cache_data(ttl=30)
    def load_all_data():
        # Usage Data ဖတ်ခြင်း
        df_usage = pd.read_csv(USAGE_CSV_URL)
        if 'Date' in df_usage.columns:
            df_usage['Date'] = pd.to_datetime(df_usage['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
        # Out Data ဖတ်ခြင်း
        df_out = pd.read_csv(OUT_CSV_URL)
        if 'Date' in df_out.columns:
            df_out['Date'] = pd.to_datetime(df_out['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
        return df_usage, df_out

    df_usage, df_out = None, None
    try:
        df_usage, df_out = load_all_data()
    except Exception as e:
        st.error(f"❌ Sheet ဒေတာချက်ဆက်မှု အဆင်မပြေပါ- {e}")

    if df_usage is not None and df_out is not None:
        
        # --- [၁] ကော်လံအမည်များ ညှိနှိုင်းခြင်း (Sleeve Column အတွက် Dynamic ရှာဖွေခြင်း) ---
        sleeve_col_in_sheet = None
        possible_sleeve_names = ['Sleeves with 2 steels', 'Sleeve with 2 Steels', 'Sleeves with 2 Steels', 'Sleeve with 2 steels']
        for col in df_usage.columns:
            if col.strip() in possible_sleeve_names:
                sleeve_col_in_sheet = col
                break
        if not sleeve_col_in_sheet:
            for col in df_usage.columns:
                if 'sleeve' in col.lower() and '2' in col:
                    sleeve_col_in_sheet = col
                    break
        if not sleeve_col_in_sheet:
            sleeve_col_in_sheet = 'Sleeve with 2 Steels'

        # စံသတ်မှတ်ထားသော Column Name များ
        columns_mapping = {
            'Date': 'Date',
            'Engineer Name': 'Engineer Name',
            'TKT/POI/CPE': 'TKT/POI',                        
            'Patch Cords(SC/APC) 1M': 'Patch Cords (1M)',          
            'Patch Cords(SC/APC) 1.5M': 'Patch Cords (1.5M)',
            sleeve_col_in_sheet: 'Sleeve with 2 Steels',
            'Customize (Pencil Kit , white)': 'Customize (Pencil Kit)',
            'Standard (Pencil Kit , white)': 'Standard (Pencil Kit)'
        }
        
        # Usage Sheet ကို Filter ဖြတ်ပြီး Name ပြောင်းခြင်း
        available_cols = [col for col in columns_mapping.keys() if col in df_usage.columns]
        filtered_usage = df_usage[available_cols].copy()
        filtered_usage = filtered_usage.rename(columns={col: columns_mapping[col] for col in available_cols})

        # --- [၂] ကော်လံအမည်များ ညှိနှိုင်းခြင်း (Out Sheet) ---
