import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics  # 👈 ဝင်ကြည့်သူ ခြေရာခံစနစ်ကို ပြန်ထည့်သွင်းခြင်း

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်သော အခင်းအကျင်း)
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 📊 ဝင်ရောက်ကြည့်ရှုသူများကို စတင်ခြေရာခံခြင်း
with streamlit_analytics.track():

    # 🎨 ဇယားကို Screen အတင်းမညှစ်ဘဲ စာလုံးအရှည်အတိုင်း တစ်ကြောင်းတည်း (Center) ပို့ပေးမည့် CSS
    st.html("""
    <style>
        /* ၁။ ဇယားတစ်ခုလုံးကို ဖုန်းပေါ်တွင် မညှပ်သွားစေဘဲ ဘေးတိုက်ရွှေ့ကြည့်နိုင်အောင် ပြုလုပ်ခြင်း */
        div[data-testid="stTable"] {
            overflow-x: auto !important;
            display: block !important;
            width: 100% !important;
        }
        
        /* ၂။ ကော်လံများကို Screen အကျယ်အတိုင်း ညှစ်မထားဘဲ စာလုံးအလိုက် အလိုအလျောက် ဆွဲဆန့်စေခြင်း */
        div[data-testid="stTable"] table {
            table-layout: auto !important;
            width: auto !important;
            min-width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            border-collapse: collapse !important;
        }

        /* ၃။ Headers (ခေါင်းစဉ်များ) ကို တစ်ကြောင်းတည်း အလယ်ပို့ခြင်း */
        div[data-testid="stTable"] th,
        div[data-testid="stTable"] th * {
            text-align: center !important;
            vertical-align: middle !important;
            white-space: nowrap !important;
            word-break: keep-all !important;
        }
        
        div[data-testid="stTable"] th {
            background-color: #f0f2f6 !important;
            padding: 12px 20px !important;
        }
        
        /* ၄။ Cells (ဒေတာများ) ကို တစ်ကြောင်းတည်း အလယ်ပို့ခြင်း */
        div[data-testid="stTable"] td,
        div[data-testid="stTable"] td * {
            text-align: center !important;
            vertical-align: middle !important;
            white-space: nowrap !important;
            word-break: keep-all !important;
        }
        
        div[data-testid="stTable"] td {
            padding: 10px 20px !important;
        }
    </style>
    """)

    # App Header
    st.markdown("<h3 style='text-align: center;'>📱 Eng Usage Checker</h3>", unsafe_allow_html=True)

    # ⚠️ သင်၏ Google Sheet CSV Link
    GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc/gviz/tq?tqx=out:csv"

    @st.cache_data(ttl=30)
    def load_data():
        df = pd.read_csv(GSHEET_CSV_URL)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        return df

    df = None
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")

    if df is not None:
        sleeve_col_in_sheet = None
        possible_sleeve_names = ['Sleeves with 2 steels', 'Sleeve with 2 Steels', 'Sleeves with 2 Steels', 'Sleeve with 2 steels']
        
        for col in df.columns:
            if col.strip() in possible_sleeve_names:
                sleeve_col_in_sheet = col
                break
                
        if not sleeve_col_in_sheet:
            for col in df.columns:
                if 'sleeve' in col.lower() and '2' in col:
                    sleeve_col_in_sheet = col
                    break
                    
        if not sleeve_col_in_sheet:
            sleeve_col_in_sheet = 'Sleeve with 2 Steels'

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
        
        available_cols = [col for col in columns_mapping.keys() if col in df.columns]
        filtered_df = df[available_cols].copy()
        filtered_df = filtered_df.rename(columns={col: columns_mapping[col] for col in available_cols})

        col1, col2 = st.columns(2)
        
        with col1:
            engineers_list = sorted(filtered_df['Engineer Name'].dropna().unique())
            selected_engineer = st.selectbox(
                "♻️ Filter by Engineer Name:",
                options=["All Engineers"] + list(engineers_list)
            )
            
        with col2:
            dates_list = sorted(filtered_df['Date'].dropna().unique(), reverse=True)
            selected_date = st.selectbox(
                "📅 Filter by Date:",
                options=["All Dates"] + list(dates_list)
            )

        result_df = filtered_df.copy()
        
        if selected_engineer != "All Engineers":
            result_df = result_df[result_df['Engineer Name'] == selected_engineer]
            
        if selected_date != "All Dates":
            result_df = result_df[result_df['Date'] == selected_date]

        st.divider()

        if not result_df.empty:
            st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📊 Engineers R1-Link Table</h3>", unsafe_allow_html=True)
            
            formatted_df = result_df.copy()
            for col in formatted_df.select_dtypes(include='number').columns:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{int(x)}" if x % 1 == 0 else f"{x:.1f}")
                
            st.table(formatted_df)
            
            total_rows = len(result_df)
            st.markdown(f"""
            <div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; border: 1px solid #c3e6cb; margin-top: 10px; margin-bottom: 25px;'>
                ✅ Total Upload = {total_rows}
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") 
            st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📈 Total Used Summary</h3>", unsafe_allow_html=True)
            
            numeric_cols = result_df.select_dtypes(include='number').columns
            
            if not numeric_cols.empty:
                summary_list = []
                for col in numeric_cols:
                    total_val = result_df[col].sum()
                    if total_val % 1 == 0:
                        formatted_val = f"{int(total_val)}"
                    else:
                        formatted_val = f"{total_val:.1f}"
                        
                    summary_list.append({'Accessories': col, 'Total Usage': formatted_val})
                
                summary_table = pd.DataFrame(summary_list)
                st.table(summary_table)
                
        else:
            st.warning("⚠️ ရွေးချယ်ထားသော အချက်အလက်များနှင့် ကိုက်ညီသည့် မှတ်တမ်း မရှိသေးပါ။")
