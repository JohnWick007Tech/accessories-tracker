import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics

# Page Configuration
st.set_page_config(page_title="Accessories Tracker", layout="centered", initial_sidebar_state="collapsed")

with streamlit_analytics.track():
    st.markdown("<h3 style='text-align: center;'>📱 Eng Usage Checker</h3>", unsafe_allow_html=True)

    # ⚠️ Google Sheet URLs
    BASE_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc"
    USAGE_CSV_URL = f"{BASE_URL}/export?format=csv&gid=0"
    OUT_CSV_URL = f"{BASE_URL}/export?format=csv&gid=147444867"

    @st.cache_data(ttl=30)
    def load_all_data():
        df_usage = pd.read_csv(USAGE_CSV_URL)
        df_out = pd.read_csv(OUT_CSV_URL)
        for df in [df_usage, df_out]:
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        return df_usage, df_out

    df_usage, df_out = load_all_data()

    # Column Mapping
    columns_mapping = {
        'Date': 'Date', 'Engineer Name': 'Engineer Name', 'TKT/POI/CPE': 'TKT/POI',
        'Patch Cords(SC/APC) 1M': 'PC(1M)', 'Patch Cords(SC/APC) 1.5M': 'PC(1.5M)',
        'Sleeve with 2 Steels': '2 Sleeves', 'Customize (Pencil Kit , white)': 'Customize PK',
        'Standard (Pencil Kit , white)': 'Standard PK'
    }
    
    filtered_usage = df_usage.rename(columns=columns_mapping)
    filtered_out = df_out.rename(columns=columns_mapping)

    # UI Filters
    col1, col2 = st.columns(2)
    with col1:
        selected_engineer = st.selectbox("♻️ Filter by Engineer Name:", options=["All Engineers"] + sorted(filtered_usage['Engineer Name'].dropna().unique().tolist()))
    with col2:
        selected_date = st.selectbox("📅 Filter by Date:", options=["All Dates"] + sorted(filtered_usage['Date'].dropna().unique().tolist(), reverse=True))

    res_usage = filtered_usage.copy()
    res_out = filtered_out.copy()
    if selected_engineer != "All Engineers": res_usage = res_usage[res_usage['Engineer Name'] == selected_engineer]
    if selected_date != "All Dates": res_usage = res_usage[res_usage['Date'] == selected_date]

    st.divider()

    # R1-Link Table
    st.markdown("<h3 style='text-align: center;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
    st.dataframe(res_usage, use_container_width=True, hide_index=True)
    st.markdown(f"<div style='background-color: #d4edda; text-align: center; padding: 10px;'>✅ Total Upload = {len(res_usage)}</div>", unsafe_allow_html=True)

    # Summary Table
    st.markdown("<h3 style='text-align: center;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
    numeric_cols = ['PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']
    
    summary_data = []
    for col in numeric_cols:
        total = res_usage[col].sum() if col in res_usage.columns else 0
        out = res_out[col].sum() if col in res_out.columns else 0
        summary_data.append({'Accessories': col, 'Out': int(out), 'Total Usage': int(total), 'Return to PM': int(out - total)})
    
    summary_df = pd.DataFrame(summary_data)

    # 💡 [အရေးကြီး] Title များကို Space ထည့်ပြီး အလယ်ညှိခြင်း (CSS မပါ)
    summary_df = summary_df.rename(columns={
        'Out': '      Out      ', 
        'Total Usage': '  Total Usage  ', 
        'Return to PM': '  Return to PM  '
    })

    st.dataframe(
        summary_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Accessories": st.column_config.TextColumn("Accessories", width="medium"),
            "      Out      ": st.column_config.NumberColumn("      Out      ", format="%d"),
            "  Total Usage  ": st.column_config.NumberColumn("  Total Usage  ", format="%d"),
            "  Return to PM  ": st.column_config.NumberColumn("  Return to PM  ", format="%d"),
        }
    )
