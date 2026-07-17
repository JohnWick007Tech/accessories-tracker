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
    # သင်သတ်မှတ်ထားတဲ့ Column အမည်များကိုသာ ရွေးထုတ်ခြင်း
    required_usage_cols = ['Date', 'Engineer Name', 'TKT/POI/CPE', 'Patch Cords(SC/APC) 1M', 'Patch Cords(SC/APC) 1.5M', 'Sleeve with 2 Steels', 'Customize (Pencil Kit , white)', 'Standard (Pencil Kit , white)']
    
    # ရရှိနိုင်တဲ့ Col တွေကိုသာ စစ်ထုတ်ယူခြင်း
    res_usage = df_usage[[c for c in required_usage_cols if c in df_usage.columns]].copy()
    res_out = df_out.copy()

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
        # အလယ်ကပ်ရန်အတွက် Configuration
        config_usage = {col: st.column_config.Column(alignment="center") for col in res_usage.columns if col not in ['Date', 'Engineer Name', 'TKT/POI/CPE']}
        st.dataframe(res_usage, use_container_width=True, hide_index=True, column_config=config_usage)

        # Summary Table
        st.markdown("<h3 style='text-align: center;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
        # Summary အတွက် လိုအပ်သော Col များ
        summary_cols = ['Patch Cords(SC/APC) 1M', 'Patch Cords(SC/APC) 1.5M', 'Sleeve with 2 Steels', 'Customize (Pencil Kit , white)', 'Standard (Pencil Kit , white)']
        summary = []
        for col in summary_cols:
            if col in res_usage.columns:
                total = pd.to_numeric(res_usage[col], errors='coerce').sum()
                out = pd.to_numeric(res_out[col], errors='coerce').sum() if col in res_out.columns else 0
                summary.append({'Accessories': col, 'Out': int(out), 'Total Usage': int(total), 'Return PM': int(out - total)})
        
        if summary:
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    # --- [၂] Negative Differences Analysis ---
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #d32f2f;'>📉 Negative Differences Analysis</h4>", unsafe_allow_html=True)

    sel_diff_eng = st.selectbox("👤 Select Engineer (Diff):", ["All Engineers"] + sorted(df_diff['Eng Name'].dropna().unique().tolist()))
    
    required_diff_cols = ['Date', 'Eng Name', 'Product Name', 'Out', 'In', 'Usage From Link', 'Difference']
    res_diff = df_diff[[c for c in required_diff_cols if c in df_diff.columns]].copy()
    
    if sel_diff_eng != "All Engineers":
        res_diff = res_diff[res_diff['Eng Name'] == sel_diff_eng]
    
    res_diff = res_diff[res_diff['Difference'] < 0]
    
    if 'Remark' in df_diff.columns:
        mask = df_diff['Remark'].astype(str).str.lower() != 'done'
        res_diff = res_diff[res_diff.index.isin(df_diff[mask].index)]

    if not res_diff.empty:
        config_diff = {col: st.column_config.Column(alignment="center") for col in res_diff.columns}
        st.dataframe(res_diff, use_container_width=True, hide_index=True, height=400, column_config=config_diff)
    else:
        st.info("ℹ️ အပ်ရန်ကျန်ရှိသည့်ပစ္စည်းမရှိပါ။")
