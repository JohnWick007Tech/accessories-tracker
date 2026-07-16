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
        
        # --- [၁] Sleeve Column အမည်ကို တူညီအောင် ရှာဖွေခြင်း ---
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

        # စံသတ်မှတ်ထားသော Column Name Maps
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
        
        # Usage Sheet ကို Filter ဖြတ်ပြီး နာမည်ပြောင်းလဲခြင်း
        available_cols = [col for col in columns_mapping.keys() if col in df_usage.columns]
        filtered_usage = df_usage[available_cols].copy()
        filtered_usage = filtered_usage.rename(columns={col: columns_mapping[col] for col in available_cols})

        # Out Sheet ကို နာမည်ညှိနှိုင်းခြင်း
        available_out_cols = [col for col in columns_mapping.keys() if col in df_out.columns]
        filtered_out = df_out[available_out_cols].copy()
        filtered_out = filtered_out.rename(columns={col: columns_mapping[col] for col in available_out_cols})

        # --- Dropdowns ဆောက်ခြင်း ---
        col1, col2 = st.columns(2)
        with col1:
            engineers_list = sorted(filtered_usage['Engineer Name'].dropna().unique())
            selected_engineer = st.selectbox(
                "♻️ Filter by Engineer Name:",
                options=["All Engineers"] + list(engineers_list)
            )
            
        with col2:
            dates_list = sorted(filtered_usage['Date'].dropna().unique(), reverse=True)
            selected_date = st.selectbox(
                "📅 Filter by Date:",
                options=["All Dates"] + list(dates_list)
            )

        # --- ဒေတာ စစ်ထုတ်ခြင်း (Filter) ---
        res_usage = filtered_usage.copy()
        res_out = filtered_out.copy()
        
        if selected_engineer != "All Engineers":
            res_usage = res_usage[res_usage['Engineer Name'] == selected_engineer]
            res_out = res_out[res_out['Engineer Name'] == selected_engineer]
            
        if selected_date != "All Dates":
            res_usage = res_usage[res_usage['Date'] == selected_date]
            res_out = res_out[res_out['Date'] == selected_date]

        st.divider()

        # --- [၃] Engineers R1-Link Table ပြသခြင်း ---
        if not res_usage.empty:
            st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
            
            formatted_df = res_usage.copy()
            # ကိန်းဂဏန်းများကို သေသပ်အောင် ပြင်ဆင်ခြင်း
            for col in formatted_df.select_dtypes(include='number').columns:
                formatted_df[col] = formatted_df[col].apply(lambda x: int(x) if x % 1 == 0 else x)
            
            # TKT/POI Duplicate ရှာဖွေပြီး အရောင်ခြယ်ရန် Function
            def highlight_duplicates(column):
                is_dup = column.duplicated(keep=False) & column.notna() & (column != '')
                return ['background-color: #f8d7da; color: #721c24; font-weight: bold;' if v else '' for v in is_dup]

            styled_df = formatted_df.style.apply(highlight_duplicates, subset=['TKT/POI'])
            
            # 💡 [ပြင်ဆင်ချက်] အနီရောင်ကွက်ထဲက ကော်လံတွေကို ဘယ်ကပ် (left) ထားပြီး၊ ပစ္စည်းအရေအတွက်တွေကိုပဲ အလယ် (center) ညှိခြင်း
            config_df = {
                'Date': st.column_config.Column(alignment="left"),
                'Engineer Name': st.column_config.Column(alignment="left"),
                'TKT/POI': st.column_config.Column(alignment="left"),
                'PC(1M)': st.column_config.Column(alignment="center"),
                'PC(1.5M)': st.column_config.Column(alignment="center"),
                '2 Sleeves': st.column_config.Column(alignment="center"),
                'Customize PK': st.column_config.Column(alignment="center"),
                'Standard PK': st.column_config.Column(alignment="center")
            }
                
            st.dataframe(
                styled_df, 
                use_container_width=True, 
                hide_index=True,
                column_config=config_df
            )
            
            total_rows = len(res_usage)
            st.markdown(f"""
            <div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; border: 1px solid #c3e6cb; margin-top: 10px; margin-bottom: 25px;'>
                ✅ Total Upload = {total_rows}
            </div>
            """, unsafe_allow_html=True)
            
            # --- [၄] Total Used & Out & Return to PM Summary ပြသခြင်း ---
            st.write("") 
            st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📈 Total Usage Summary</h3>", unsafe_allow_html=True)
            
            numeric_cols = [col for col in ['PC(1M)', 'PC(1.5M)', '2 Sleeves', 'Customize PK', 'Standard PK'] if col in res_usage.columns]
            
            if numeric_cols:
                summary_data = []
                for col in numeric_cols:
                    total_val = pd.to_numeric(res_usage[col], errors='coerce').sum()
                    formatted_val = int(total_val) if total_val % 1 == 0 else round(total_val, 1)
                    
                    out_val = 0
                    if col in res_out.columns:
                        out_val = pd.to_numeric(res_out[col], errors='coerce').sum()
                    formatted_out = int(out_val) if out_val % 1 == 0 else round(out_val, 1)
                    
                    return_val = out_val - total_val
                    formatted_return = int(return_val) if return_val % 1 == 0 else round(return_val, 1)
                        
                    summary_data.append({
                        'Accessories': col, 
                        'Out': formatted_out,
                        'Total Usage': formatted_val,
                        'Return PM': formatted_return
                    })
                
                summary_table = pd.DataFrame(summary_data)
                
                # 💡 ဇယားထဲက ကော်လံတစ်ခုချင်းစီကို အစဉ်လိုက် loop ပတ်ပြီး 
                # ပထမဆုံးကော်လံ (Index 0) ကိုပဲ ဘယ်ကပ်ပြီး၊ ကျန်တဲ့ Out အပါအဝင် ကော်လံအားလုံးကို Center အသေညှိခြင်း
                config_summary = {}
                for idx, col in enumerate(summary_table.columns):
                    if idx == 0:
                        config_summary[col] = st.column_config.TextColumn(alignment="left")
                    else:
                        # ဒေတာတွေကိုပါ Text အဖြစ်ပြောင်းပြီး Center တွန်းပို့ပါတယ်
                        summary_table[col] = summary_table[col].astype(str)
                        config_summary[col] = st.column_config.TextColumn(alignment="center")
                
                # DataFrame ပြသခြင်း
                st.dataframe(
                    summary_table, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config=config_summary
                )
                
        else:
            st.warning("⚠️ ရွေးချယ်ထားသော အချက်အလက်များနှင့် ကိုက်ညီသည့် မှတ်တမ်း မရှိသေးပါ။")
