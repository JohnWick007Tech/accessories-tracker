import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics

# Page Configuration
st.set_page_config(page_title="Accessories Tracker", layout="centered", initial_sidebar_state="collapsed")

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

    # --- [၁] Usage Data Setup ---
    sleeve_col = next((c for c in df_usage.columns if 'sleeve' in c.lower()), 'Sleeve with 2 Steels')
    cols_map = {'Date': 'Date', 'Engineer Name': 'Engineer Name', 'TKT/POI/CPE': 'TKT/POI', 
                'Patch Cords(SC/APC) 1M': 'PC(1M)', 'Patch Cords(SC/APC) 1.5M': 'PC(1.5M)', 
                sleeve_col: '2 Sleeves', 'Customize (Pencil Kit , white)': 'Customize PK', 
                'Standard (Pencil Kit , white)': 'Standard PK'}
    
    # ရွေးထုတ်ထားသော Column များ
    required_usage_cols = ['Date', 'Engineer Name', 'TKT/POI', 'PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']
    
    res_usage = df_usage.rename(columns=cols_map)
    # လိုအပ်သော column များသာ ရွေးထုတ်ခြင်း
    res_usage = res_usage[[c for c in required_usage_cols if c in res_usage.columns]]
    res_out = df_out.rename(columns=cols_map)

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
    if not res_usage.empty:
        st.markdown("<h3 style='text-align: center;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
        # Usage Table Config
        usage_config = {col: st.column_config.Column(alignment="center") for col in res_usage.columns if col not in ['Date', 'Engineer Name', 'TKT/POI']}
        st.dataframe(res_usage, use_container_width=True, hide_index=True, column_config=usage_config)

        st.markdown("<h3 style='text-align: center;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
        summary = []
        for col in ['PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']:
            if col in res_usage.columns:
                total = pd.to_numeric(res_usage[col], errors='coerce').sum()
                out = pd.to_numeric(res_out[col], errors='coerce').sum() if col in res_out.columns else 0
                summary.append({'Accessories': col, 'Out': int(out), 'Total Usage': int(total), 'Return PM': int(out - total)})
        
        summary_df = pd.DataFrame(summary)
        summary_config = {col: st.column_config.Column(alignment="center") for col in summary_df.columns if col != 'Accessories'}
        st.dataframe(summary_df, use_container_width=True, hide_index=True, column_config=summary_config)

    # --- [၂] Negative Differences Analysis ---
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #d32f2f;'>📉 ဒီနေ့မပါ ငါးရက်အတွင်း PMသို့အပ်ရန်ကျန်ရှိစာရင်း Difference များကိုကြည့်ပါ", unsafe_allow_html=True)

    sel_diff_eng = st.selectbox("👤 Select Engineer (Diff):", ["All Engineers"] + sorted(df_diff['Eng Name'].dropna().unique().tolist()))
    
    required_cols = ['Date', 'Eng Name', 'Product Name', 'Out', 'In', 'Usage From Link', 'Difference']
    res_diff = df_diff[[c for c in required_cols if c in df_diff.columns]].copy()
    
    if sel_diff_eng != "All Engineers":
        res_diff = res_diff[res_diff['Eng Name'] == sel_diff_eng]
    
    res_diff = res_diff[res_diff['Difference'] < 0]
    
    if 'Remark' in df_diff.columns:
        mask = df_diff['Remark'].astype(str).str.lower() != 'done'
        res_diff = res_diff[res_diff.index.isin(df_diff[mask].index)]

    if not res_diff.empty:
        diff_config = {
            'Eng Name': st.column_config.Column(alignment="left"),
            'Product Name': st.column_config.Column(alignment="left"),
            'Date': st.column_config.Column(alignment="center"),
            'Out': st.column_config.Column(alignment="center"),
            'In': st.column_config.Column(alignment="center"),
            'Usage From Link': st.column_config.Column(alignment="center"),
            'Difference': st.column_config.Column(alignment="center")
        }
        st.dataframe(res_diff, use_container_width=True, hide_index=True, height=400, column_config=diff_config)
    else:
        st.info("ℹ️ အပ်ရန်ကျန်ရှိသည့်ပစ္စည်းမရှိပါ။")
