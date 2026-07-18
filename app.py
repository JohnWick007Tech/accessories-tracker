import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics

# Page Configuration
st.set_page_config(page_title="Accessories Tracker", layout="centered", initial_sidebar_state="collapsed")

with streamlit_analytics.track():
    st.markdown("<h3 style='text-align: center;'>📱 Eng Usage Checker</h3>", unsafe_allow_html=True)

    BASE_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc"
    
    @st.cache_data(ttl=60)
    def load_all_data():
        df_usage = pd.read_csv(f"{BASE_URL}/export?format=csv&gid=0")
        df_out = pd.read_csv(f"{BASE_URL}/export?format=csv&gid=147444867")
        df_diff = pd.read_csv(f"{BASE_URL}/export?format=csv&gid=1623311186")
        return df_usage, df_out, df_diff

    try:
        df_usage, df_out, df_diff = load_all_data()
    except Exception as e:
        st.error(f"❌ ဒေတာချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")
        st.stop()

    # --- Data Cleaning & Mapping ---
    def clean_and_map(df):
        df = df.copy()
        df.columns = df.columns.str.strip()
        # Sleeve column ရှာဖွေခြင်း
        sleeve_col = next((c for c in df.columns if 'sleeve' in c.lower()), None)
        
        mapping = {
            'Engineer Name': 'Engineer Name',
            'TKT/POI/CPE': 'TKT/POI',
            'Patch Cords(SC/APC) 1M': 'PC(1M)',
            'Patch Cords(SC/APC) 1.5M': 'PC(1.5M)',
            'Customize (Pencil Kit , white)': 'Customize PK',
            'Standard (Pencil Kit , white)': 'Standard PK'
        }
        if sleeve_col: mapping[sleeve_col] = '2 Sleeves'
        
        df = df.rename(columns=mapping)
        # လိုအပ်သော columns များသာ ထားရှိခြင်း
        cols = ['Date', 'Engineer Name', 'TKT/POI', 'PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]
        # Numeric ပိုင်းအတွက် 0 ဖြည့်ခြင်း
        for col in existing_cols:
            if col not in ['Date', 'Engineer Name', 'TKT/POI']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df

    res_usage = clean_and_map(df_usage)
    res_out = clean_and_map(df_out)

    # Filter
    engs = ["All Engineers"] + sorted([str(x) for x in res_usage['Engineer Name'].unique() if pd.notna(x)])
    sel_eng = st.selectbox("♻️ Filter by Engineer Name:", engs)
    
    if sel_eng != "All Engineers":
        res_usage = res_usage[res_usage['Engineer Name'] == sel_eng]
        res_out = res_out[res_out['Engineer Name'] == sel_eng]

    # --- Tables ---
    st.divider()
    st.markdown("<h3 style='text-align: center;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
    st.dataframe(res_usage, use_container_width=True, hide_index=True, 
                 column_config={c: st.column_config.Column(alignment="center") for c in res_usage.columns})

    st.markdown("<h3 style='text-align: center;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
    summary_data = []
    for col in ['PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']:
        total = res_usage[col].sum() if col in res_usage.columns else 0
        out = res_out[col].sum() if col in res_out.columns else 0
        summary_data.append({'Accessories': col, 'Out': int(out), 'Total Usage': int(total), 'Return PM': int(out - total)})
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True, 
                 column_config={c: st.column_config.Column(alignment="center") for c in summary_df.columns})

    # --- Negative Differences ---
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #d32f2f;'>📉 Return to PM List</h4>", unsafe_allow_html=True)
    
    # Unnamed Columns ဖယ်ရှားပြီး Difference စစ်ဆေးခြင်း
    res_diff = df_diff.loc[:, ~df_diff.columns.str.contains('^Unnamed')]
    if 'Difference' in res_diff.columns:
        res_diff = res_diff[res_diff['Difference'] < 0]
    
    st.dataframe(res_diff, use_container_width=True, hide_index=True, 
                 column_config={c: st.column_config.Column(alignment="center") for c in res_diff.columns})
