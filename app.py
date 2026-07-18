import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics

# Page Configuration
st.set_page_config(page_title="Accessories Tracker", layout="centered", initial_sidebar_state="collapsed")

# CSS - Branding နှင့် Toolbar များဖျောက်ရန်
st.markdown("""
    <style>
        [data-testid="stDataFrameToolbar"] { display: none !important; }
        #MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }
        div[data-testid="stAppDeployButton"], div[data-testid="stDecoration"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

with streamlit_analytics.track():
    st.markdown("<h3 style='text-align: center;'>📱 Eng Usage Checker</h3>", unsafe_allow_html=True)

    BASE_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc"
    USAGE_CSV_URL = f"{BASE_URL}/export?format=csv&gid=0"
    OUT_CSV_URL = f"{BASE_URL}/export?format=csv&gid=147444867"
    DIFF_CSV_URL = f"{BASE_URL}/export?format=csv&gid=1623311186"

    @st.cache_data(ttl=30)
    def load_all_data():
        df_usage = pd.read_csv(USAGE_CSV_URL)
        df_out = pd.read_csv(OUT_CSV_URL)
        df_diff = pd.read_csv(DIFF_CSV_URL)
        for df in [df_usage, df_out, df_diff]:
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        return df_usage, df_out, df_diff

    try:
        df_usage, df_out, df_diff = load_all_data()
    except Exception as e:
        st.error(f"❌ ဒေတာချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")
        st.stop()

    # --- [၁] Data Standardization ---
    def standardize_df(df):
        new_cols = {}
        for col in df.columns:
            c = col.strip().lower()
            if 'sleeve' in c and '2' in c: new_cols[col] = '2 Sleeves'
            elif 'patch cords' in c and '1m' in c: new_cols[col] = 'PC(1M)'
            elif 'patch cords' in c and '1.5m' in c: new_cols[col] = 'PC(1.5M)'
            elif 'customize' in c: new_cols[col] = 'Customize PK'
            elif 'standard' in c: new_cols[col] = 'Standard PK'
            elif 'tkt' in c or 'poi' in c or 'cpe' in c: new_cols[col] = 'TKT/POI'
            else: new_cols[col] = col.strip()
        return df.rename(columns=new_cols)

    res_usage = standardize_df(df_usage.copy())
    res_out = standardize_df(df_out.copy())
    
    required_cols = ['Date', 'Engineer Name', 'TKT/POI', 'PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']
    
    # Missing columns ထည့်ပေးခြင်း
    for col in required_cols:
        if col not in res_usage.columns: res_usage[col] = 0
        if col not in res_out.columns: res_out[col] = 0

    res_usage = res_usage[required_cols]
    res_out = res_out[required_cols]

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        sel_eng = st.selectbox("♻️ Filter by Engineer Name:", ["All Engineers"] + sorted(res_usage['Engineer Name'].dropna().unique().tolist()))
    with col2:
        sel_date = st.selectbox("📅 Filter by Date:", ["All Dates"] + sorted(res_usage['Date'].dropna().unique().tolist(), reverse=True))

    if sel_eng != "All Engineers":
        res_usage = res_usage[res_usage['Engineer Name'] == sel_eng]
        res_out = res_out[res_out['Engineer Name'] == sel_eng]
    if sel_date != "All Dates":
        res_usage = res_usage[res_usage['Date'] == sel_date]
        res_out = res_out[res_out['Date'] == sel_date]

    st.divider()

    # R1-Link Table
    if not res_usage.empty:
        st.markdown("<h3 style='text-align: center;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
        usage_config = {col: st.column_config.Column(alignment="center") for col in res_usage.columns if col not in ['Date', 'Engineer Name', 'TKT/POI']}
        st.dataframe(res_usage, use_container_width=True, hide_index=True, column_config=usage_config)

        # Summary Table
        st.markdown("<h3 style='text-align: center;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
        summary = []
        for col in ['PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']:
            total = pd.to_numeric(res_usage[col], errors='coerce').sum()
            out = pd.to_numeric(res_out[col], errors='coerce').sum()
            summary.append({'Accessories': col, 'Out': int(out), 'Total Usage': int(total), 'Return PM': int(out - total)})
        
        summary_df = pd.DataFrame(summary)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # --- [၂] Negative Differences ---
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #d32f2f;'>📉 Return to PM List</h4>", unsafe_allow_html=True)
    sel_diff_eng = st.selectbox("👤 Select Engineer (Diff):", ["All Engineers"] + sorted(df_diff['Eng Name'].dropna().unique().tolist()))
    
    res_diff = df_diff.copy()
    if sel_diff_eng != "All Engineers":
        res_diff = res_diff[res_diff['Eng Name'] == sel_diff_eng]
    res_diff = res_diff[res_diff['Difference'] < 0]
    
    if not res_diff.empty:
        st.dataframe(res_diff, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("ℹ️ အပ်ရန်ကျန်ရှိသည့်ပစ္စည်းမရှိပါ။")
