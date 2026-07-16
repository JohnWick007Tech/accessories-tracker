import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics

# Page Configuration
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 💡 Toolbar, Branding နှင့် ညာဘက်အောက်ထောင့်က အိုင်ကွန်များအားလုံးကို ဖျောက်ရန် CSS
st.markdown("""
    <style>
        /* Toolbar များကို ဖျောက်ရန် */
        [data-testid="stDataFrameToolbar"] { display: none !important; }
        
        /* ညာဘက်အောက်ထောင့် branding နှင့် ညာဘက်အပေါ်က Fork အိုင်ကွန်များ ဖျောက်ရန် */
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        header { visibility: hidden !important; }
        
        /* ညာဘက်အောက်ထောင့်က အိုင်ကွန်ကို ဖျောက်ခြင်း */
        div[data-testid="stDecoration"] { visibility: hidden !important; }
        div[data-testid="stAppDeployButton"] { visibility: hidden !important; }
        .stDeployButton { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

with streamlit_analytics.track():

    st.markdown("<h3 style='text-align: center;'>📱 Eng Usage Checker</h3>", unsafe_allow_html=True)

    # ⚠️ Google Sheet URLs
    BASE_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc"
    USAGE_CSV_URL = f"{BASE_URL}/export?format=csv&gid=0"
    OUT_CSV_URL = f"{BASE_URL}/export?format=csv&gid=147444867"

    @st.cache_data(ttl=30)
    def load_all_data():
        df_usage = pd.read_csv(USAGE_CSV_URL)
        if 'Date' in df_usage.columns:
            df_usage['Date'] = pd.to_datetime(df_usage['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
        df_out = pd.read_csv(OUT_CSV_URL)
        if 'Date' in df_out.columns:
            df_out['Date'] = pd.to_datetime(df_out['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
        return df_usage, df_out

    df_usage, df_out = None, None
    try:
        df_usage, df_out = load_all_data()
    except Exception as e:
        st.error(f"❌ Sheet ဒေတာချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")

    if df_usage is not None and df_out is not None:
        
        # Sleeve Column ရှာဖွေခြင်း
        sleeve_col_in_sheet = next((col for col in df_usage.columns if 'sleeve' in col.lower() and '2' in col), 'Sleeve with 2 Steels')

        # Column Mapping
        columns_mapping = {
            'Date': 'Date', 'Engineer Name': 'Engineer Name', 'TKT/POI/CPE': 'TKT/POI',
            'Patch Cords(SC/APC) 1M': 'PC(1M)', 'Patch Cords(SC/APC) 1.5M': 'PC(1.5M)',
            sleeve_col_in_sheet: '2 Sleeves',
            'Customize (Pencil Kit , white)': 'Customize PK',
            'Standard (Pencil Kit , white)': 'Standard PK'
        }
        
        filtered_usage = df_usage[list(columns_mapping.keys())].rename(columns=columns_mapping)
        filtered_out = df_out[[col for col in columns_mapping.keys() if col in df_out.columns]].rename(columns=columns_mapping)

        # Dropdowns
        col1, col2 = st.columns(2)
        with col1:
            selected_engineer = st.selectbox("♻️ Filter by Engineer Name:", options=["All Engineers"] + sorted(filtered_usage['Engineer Name'].dropna().unique().tolist()))
        with col2:
            selected_date = st.selectbox("📅 Filter by Date:", options=["All Dates"] + sorted(filtered_usage['Date'].dropna().unique().tolist(), reverse=True))

        res_usage = filtered_usage.copy()
        res_out = filtered_out.copy()
        if selected_engineer != "All Engineers":
            res_usage = res_usage[res_usage['Engineer Name'] == selected_engineer]
            res_out = res_out[res_out['Engineer Name'] == selected_engineer]
        if selected_date != "All Dates":
            res_usage = res_usage[res_usage['Date'] == selected_date]
            res_out = res_out[res_out['Date'] == selected_date]

        st.divider()

        # R1-Link Table
        if not res_usage.empty:
            st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
            formatted_df = res_usage.copy()
            for col in formatted_df.select_dtypes(include='number').columns:
                formatted_df[col] = formatted_df[col].apply(lambda x: int(x) if x % 1 == 0 else x)
            
            def highlight_duplicates(column):
                is_dup = column.duplicated(keep=False) & column.notna() & (column != '')
                return ['background-color: #f8d7da; color: #721c24; font-weight: bold;' if v else '' for v in is_dup]

            styled_df = formatted_df.style.apply(highlight_duplicates, subset=['TKT/POI'])
            
            config_df = {col: st.column_config.Column(alignment="center" if col not in ['Date', 'Engineer Name', 'TKT/POI'] else "left") for col in formatted_df.columns}
                
            st.dataframe(styled_df, use_container_width=True, hide_index=True, column_config=config_df)
            
            st.markdown(f"<div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-top: 10px; margin-bottom: 25px;'>✅ Total Upload = {len(res_usage)}</div>", unsafe_allow_html=True)
            
            # Summary Table
            st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
            numeric_cols = ['PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK']
            
            summary_data = []
            for col in numeric_cols:
                total_val = pd.to_numeric(res_usage[col], errors='coerce').sum() if col in res_usage.columns else 0
                out_val = pd.to_numeric(res_out[col], errors='coerce').sum() if col in res_out.columns else 0
                summary_data.append({'Accessories': col, 'Out': int(out_val), 'Total Usage': int(total_val), 'Return PM': int(out_val - total_val)})
            
            summary_table = pd.DataFrame(summary_data).rename(columns={'Out': '      Out      ', 'Total Usage': '    Total Usage    ', 'Return PM': '    Return PM    '})
            
            st.dataframe(
                summary_table, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Accessories": st.column_config.TextColumn("Accessories", width="medium"),
                    "      Out      ": st.column_config.NumberColumn("      Out      ", format="%d"),
                    "    Total Usage    ": st.column_config.NumberColumn("    Total Usage    ", format="%d"),
                    "    Return PM    ": st.column_config.NumberColumn("    Return PM    ", format="%d"),
                }
            )
        else:
            st.warning("⚠️ ရွေးချယ်ထားသော အချက်အလက်များနှင့် ကိုက်ညီသည့် မှတ်တမ်း မရှိသေးပါ။")
