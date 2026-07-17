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
    DIFF_CSV_URL = f"{BASE_URL}/export?format=csv&gid=1623311186" # Added Different Sheet

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

    # --- [၁] Sleeve Column အမည်ကို တူညီအောင် ရှာဖွေခြင်း ---
    sleeve_col_in_sheet = None
    possible_sleeve_names = ['Sleeves with 2 steels', 'Sleeve with 2 Steels', 'Sleeves with 2 Steels', 'Sleeve with 2 steels']
    for col in df_usage.columns:
        if col.strip() in possible_sleeve_names:
            sleeve_col_in_sheet = col
            break
    if not sleeve_col_in_sheet:
        sleeve_col_in_sheet = 'Sleeve with 2 Steels'

    columns_mapping = {
        'Date': 'Date',
        'Engineer Name': 'Engineer Name',
        'TKT/POI/CPE': 'TKT/POI',                  
        'Patch Cords(SC/APC) 1M': 'PC(1M)',        
        'Patch Cords(SC/APC) 1.5M': 'PC(1.5M)',
        sleeve_col_in_sheet: '2 Sleeves',
        'Customize (Pencil Kit , white)': 'Customize PK',
        'Standard (Pencil Kit , white)': 'Standard PK'
    }
    
    filtered_usage = df_usage.rename(columns={col: columns_mapping[col] for col in columns_mapping if col in df_usage.columns})
    filtered_out = df_out.rename(columns={col: columns_mapping[col] for col in columns_mapping if col in df_out.columns})

    # --- Dropdowns ---
    col1, col2 = st.columns(2)
    with col1:
        engineers_list = sorted(filtered_usage['Engineer Name'].dropna().unique())
        selected_engineer = st.selectbox("♻️ Filter by Engineer Name:", ["All Engineers"] + list(engineers_list))
    with col2:
        dates_list = sorted(filtered_usage['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("📅 Filter by Date:", ["All Dates"] + list(dates_list))

    # --- Data Filtering ---
    res_usage = filtered_usage.copy()
    res_out = filtered_out.copy()
    
    if selected_engineer != "All Engineers":
        res_usage = res_usage[res_usage['Engineer Name'] == selected_engineer]
        res_out = res_out[res_out['Engineer Name'] == selected_engineer]
    if selected_date != "All Dates":
        res_usage = res_usage[res_usage['Date'] == selected_date]
        res_out = res_out[res_out['Date'] == selected_date]

    st.divider()

    # --- [၃] Engineers R1-Link Table ---
    if not res_usage.empty:
        st.markdown("<h3 style='text-align: center;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
        st.dataframe(res_usage, use_container_width=True, hide_index=True)
        
        # --- [၄] Total Usage Summary ---
        st.markdown("<h3 style='text-align: center;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
        numeric_cols = ['PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']
        summary_data = []
        for col in numeric_cols:
            if col in res_usage.columns:
                total_val = pd.to_numeric(res_usage[col], errors='coerce').sum()
                out_val = pd.to_numeric(res_out[col], errors='coerce').sum() if col in res_out.columns else 0
                summary_data.append({'Accessories': col, 'Out': int(out_val), 'Total Usage': int(total_val), 'Return PM': int(out_val - total_val)})
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

    # --- [၅] Different Table (Newly Added) ---
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #d32f2f;'>📉 Negative Differences Analysis</h4>", unsafe_allow_html=True)
    
    # Filter: Engineer တစ်ခုတည်းသာ၊ Difference < 0၊ Remark 'Done' မဟုတ်မှ
    res_diff = df_diff.copy()
    if selected_engineer != "All Engineers":
        res_diff = res_diff[res_diff['Eng Name'] == selected_engineer]
    
    res_diff = res_diff[res_diff['Difference'] < 0]
    if 'Remark' in res_diff.columns:
        res_diff = res_diff[res_diff['Remark'].astype(str).str.lower() != 'done']
        res_diff = res_diff.drop(columns=['Remark']) # ဇယားမှာ Remark မပြရန်

    if not res_diff.empty:
        st.dataframe(res_diff, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("ℹ️ အပ်ရန်ကျန်ရှိသည့်ပစ္စည်းမရှိပါ။")
