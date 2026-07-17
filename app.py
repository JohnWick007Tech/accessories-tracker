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
    USAGE_CSV_URL = f"{BASE_URL}/export?format=csv&gid=0"
    OUT_CSV_URL = f"{BASE_URL}/export?format=csv&gid=147444867"
    DIFF_CSV_URL = f"{BASE_URL}/export?format=csv&gid=1623311186" # GID အမှန်ထည့်ပါ

    @st.cache_data(ttl=30)
    def load_all_data():
        df_usage = pd.read_csv(USAGE_CSV_URL)
        df_out = pd.read_csv(OUT_CSV_URL)
        df_diff = pd.read_csv(DIFF_CSV_URL)
        
        # Date Format ညှိခြင်း
        for df in [df_usage, df_out, df_diff]:
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
        return df_usage, df_out, df_diff

    try:
        df_usage, df_out, df_diff = load_all_data()
    except Exception as e:
        st.error(f"❌ Sheet ဒေတာချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")
        st.stop()

    # --- [၁] အပေါ်ပိုင်း (Usage) အတွက် Filter ---
    col1, col2 = st.columns(2)
    eng_col = 'Engineer Name' if 'Engineer Name' in df_usage.columns else 'Eng Name'
    
    with col1:
        engineers_list = sorted(df_usage[eng_col].dropna().unique())
        sel_eng = st.selectbox("♻️ Filter by Engineer Name:", ["All Engineers"] + list(engineers_list))
    with col2:
        dates_list = sorted(df_usage['Date'].dropna().unique(), reverse=True)
        sel_date = st.selectbox("📅 Filter by Date:", ["All Dates"] + list(dates_list))

    # --- [၂] အပေါ်ပိုင်း Data ပြသခြင်း ---
    res_usage = df_usage.copy()
    if sel_eng != "All Engineers": res_usage = res_usage[res_usage[eng_col] == sel_eng]
    if sel_date != "All Dates": res_usage = res_usage[res_usage['Date'] == sel_date]

    st.divider()
    if not res_usage.empty:
        st.markdown("<h3 style='text-align: center;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
        # height=400 ထည့်ခြင်းဖြင့် Table အရှည်ကြီးဖြစ်သွားလျှင် Header ကို Freeze လုပ်ပေးပါသည်
        st.dataframe(res_usage, use_container_width=True, hide_index=True, height=400)
    else:
        st.warning("⚠️ မှတ်တမ်း မရှိပါ။")

    # --- [၃] Negative Differences Analysis (သီးသန့် Filter ဖြင့်) ---
    st.divider()
    st.markdown("<h3 style='text-align: center; color: #d32f2f;'>📉 PM သို့ပြန်အပ်ရန်ကျန်သောပစ္စည်းများ ( 5 ရက်စာဒီနေ့မပါဝင်ပါ )</h3>", unsafe_allow_html=True)
    
    # လိုချင်တဲ့ Column တွေကိုပဲ သေချာရွေးထုတ်ခြင်း
    required_cols = ['Date', 'Eng Name', 'Product Name', 'Out', 'In', 'Usage From Link', 'Difference']
    available_cols = [c for c in required_cols if c in df_diff.columns]
    res_diff = df_diff[available_cols].copy()
    
    diff_col1, diff_col2 = st.columns(2)
    with diff_col1:
        diff_engs = sorted(res_diff['Eng Name'].dropna().unique())
        sel_diff_eng = st.selectbox("👤 Select Engineer (Diff):", ["All Engineers"] + list(diff_engs))
    with diff_col2:
        diff_dates = sorted(res_diff['Date'].dropna().unique(), reverse=True)
        sel_diff_date = st.selectbox("🗓 Select Date (Diff):", ["All Dates"] + list(diff_dates))
    
    # Filter လုပ်ခြင်း
    if sel_diff_eng != "All Engineers": res_diff = res_diff[res_diff['Eng Name'] == sel_diff_eng]
    if sel_diff_date != "All Dates": res_diff = res_diff[res_diff['Date'] == sel_diff_date]
    
    # Difference < 0 ကို စစ်ထုတ်ခြင်း
    res_diff = res_diff[res_diff['Difference'] < 0]
    
    if not res_diff.empty:
        # height=400 ထည့်ခြင်းဖြင့် Table အရှည်ကြီးဖြစ်သွားလျှင် Header ကို Freeze လုပ်ပေးပါသည်
        st.dataframe(res_diff, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("ℹ️ ရွေးချယ်ထားသော အချက်အလက်များတွင် Negative Difference မရှိပါ။")
