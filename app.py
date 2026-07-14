import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🎨 CSS
st.html("""
<style>
    div[data-testid="stTable"] {
        overflow-x: auto !important;
        display: block !important;
        width: 100% !important;
    }
    div[data-testid="stTable"] table {
        table-layout: auto !important;
        width: auto !important;
        min-width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        border-collapse: collapse !important;
    }
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
st.markdown("<h2 style='text-align: center;'>📱 Eng Usage Tracker</h2>", unsafe_allow_html=True)

# ⚠️ သင်၏ Google Sheet Link မူရင်း
GSHEET_BASE_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc"

USAGE_TAB_NAME = "EngUsageTracker"
OUT_TAB_NAME = "Out Of PM"

USAGE_CSV_URL = f"{GSHEET_BASE_URL}/gviz/tq?tqx=out:csv&sheet={USAGE_TAB_NAME}"
OUT_CSV_URL = f"{GSHEET_BASE_URL}/gviz/tq?tqx=out:csv&sheet={OUT_TAB_NAME}"

@st.cache_data(ttl=30)
def load_usage_data():
    df = pd.read_csv(USAGE_CSV_URL)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

@st.cache_data(ttl=30)
def load_out_data():
    try:
        df_out = pd.read_csv(OUT_CSV_URL)
        if 'Date' in df_out.columns:
            # 🔹 14-Jul-26 ကဲ့သို့သော စာသား format ကို တိကျမှန်ကန်စွာ ကောက်ယူနိုင်ရန် explicit format ဖြင့် ပြောင်းလဲခြင်း
            # %d-%b-%y သည် ရက်စွဲ-လအတိုကောက်-နှစ်အကျဉ်း (ဥပမာ 14-Jul-26 -> 2026-07-14) ကို ကွက်တိရစေပါသည်
            df_out['Date'] = pd.to_datetime(df_out['Date'], format='%d-%b-%y', errors='coerce').dt.strftime('%Y-%m-%d')
        return df_out
    except Exception as e:
        return None

# ဒေတာဆွဲယူခြင်း
df = None
df_out = None
try:
    df = load_usage_data()
    df_out = load_out_data()
except Exception as e:
    st.error(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")

if df is not None:
    
    # 🔍 Sleeve Column နာမည်ရှာဖွေခြင်း logic
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

    # ၁။ ကော်လံများ စစ်ထုတ်ခြင်း
    columns_mapping = {
        'Date': 'Date',
        'Engineer Name': 'Engineer Name',
        'TKT/POI/CPE': 'TKT/POI/CPE',                         
        'Patch Cords(SC/APC) 1M': 'Patch Cords (1M)',          
        'Patch Cords(SC/APC) 1.5M': 'Patch Cords (1.5M)',
        sleeve_col_in_sheet: 'Sleeve with 2 Steels',
        'Customize (Pencil Kit , white)': 'Customize (Pencil Kit)',
        'Standard (Pencil Kit , white)': 'Standard (Pencil Kit)'
    }
    
    available_cols = [col for col in columns_mapping.keys() if col in df.columns]
    filtered_df = df[available_cols].copy()
    filtered_df = filtered_df.rename(columns={col: columns_mapping[col] for col in available_cols})

    # ၂။ Dropdown ရွေးချယ်မှုအပိုင်း
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

    # ၃။ Filter Logic (မူရင်း ဇယားတွက်ရန်)
    result_df = filtered_df.copy()
    
    if selected_engineer != "All Engineers":
        result_df = result_df[result_df['Engineer Name'] == selected_engineer]
        
    if selected_date != "All Dates":
        result_df = result_df[result_df['Date'] == selected_date]

    st.divider()

    # ၄။ ရလဒ်အား Table ဖြင့် ပြသခြင်း
    if not result_df.empty:
        st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📊 Engineers Usages Table</h3>", unsafe_allow_html=True)
        
        formatted_df = result_df.copy()
        for col in formatted_df.select_dtypes(include='number').columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{int(x)}" if x % 1 == 0 else f"{x:.1f}")
            
        st.table(formatted_df)
        
        # ၅။ Summary အပိုင်းတွက်ချက်ခြင်း
        st.write("") 
        st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>📈 Total Used Summary</h3>", unsafe_allow_html=True)
        
        numeric_cols = result_df.select_dtypes(include='number').columns
        
        if not numeric_cols.empty:
            summary_list = []
            
            # Product Name Mapping Dictionaries
            product_name_mapping = {
                'SC-APC,SM,SX 3.0MM (1M)': 'Patch Cords (1M)',
                'Sleeves with 2 steels': 'Sleeve with 2 Steels',
                'Pencil Kit (Standard)': 'Standard (Pencil Kit)',
                'Pencil Kit (Customized)': 'Customize (Pencil Kit)',
                'Customize (Pencil Kit)': 'Customize (Pencil Kit)',
                'Patch Cords (1.5M)': 'Patch Cords (1.5M)'
            }
            
            for col in numeric_cols:
                # က။ မူရင်း သုံးစွဲမှု စုစုပေါင်း (Total Usage)
                total_usage_val = result_df[col].sum()
                
                # ခ။ Out Of PM ထဲက 'Out' ရှာဖွေခြင်း logic
                total_out_val = 0
                if df_out is not None and 'Product Name' in df_out.columns and 'Out' in df_out.columns:
                    temp_out_df = df_out.copy()
                    
                    # နေရာလွတ်များဖယ်ပြီး mapping ညှိခြင်း
                    temp_out_df['Mapped_Product'] = temp_out_df['Product Name'].astype(str).str.strip().map(product_name_mapping).fillna(temp_out_df['Product Name'].astype(str).str.strip())
                    
                    item_out_df = temp_out_df[temp_out_df['Mapped_Product'].str.lower() == col.strip().lower()]
                    
                    # Engineer Filter စစ်ဆေးခြင်း
                    if selected_engineer != "All Engineers" and 'Eng Name' in item_out_df.columns:
                        # နာမည် အတိအကျတူညီမှု သို့မဟုတ် ID မတူညီပါက Substring ပါဝင်မှုဖြင့် filter လုပ်သည်
                        clean_eng_name = selected_engineer.split('-')[0].strip()
                        item_out_df = item_out_df[
                            (item_out_df['Eng Name'].astype(str).str.strip() == selected_engineer) | 
                            (item_out_df['Eng Name'].astype(str).str.contains(clean_eng_name, case=False, na=False))
                        ]
                        
                    # Date Filter စစ်ဆေးခြင်း
                    if selected_date != "All Dates" and 'Date' in item_out_df.columns:
                        item_out_df = item_out_df[item_out_df['Date'] == selected_date]
                        
                    # Out တန်ဖိုးများကို ပေါင်းယူခြင်း
                    total_out_val = pd.to_numeric(item_out_df['Out'], errors='coerce').sum()
                
                # ဂ။ Return to PM = Out - Total Usage တွက်ချက်ခြင်း
                return_to_pm_val = total_out_val - total_usage_val
                
                def format_num(val):
                    if val % 1 == 0:
                        return f"{int(val)}"
                    return f"{val:.1f}"
                
                summary_list.append({
                    'Accessories': col, 
                    'Total Out (Store)': format_num(total_out_val),
                    'Total Usage (Field)': format_num(total_usage_val),
                    'Return to PM Usage': format_num(return_to_pm_val)
                })
            
            summary_table = pd.DataFrame(summary_list)
            st.table(summary_table)
            
    else:
        st.warning("⚠️ ရွေးချယ်ထားသော အချက်အလက်များနှင့် ကိုက်ညီသည့် မှတ်တမ်း မရှိသေးပါ။")
