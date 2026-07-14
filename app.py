import streamlit as st
import pandas as pd

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်သော အခင်းအကျင်း)
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
        table-layout: auto !important; /* စာလုံးအရှည်အတိုင်း ကော်လံ ကျယ်ထွက်သွားစေရန် */
        width: auto !important;
        min-width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        border-collapse: collapse !important;
    }

    /* ၃။ Headers (ခေါင်းစဉ်များ) ကို တစ်ကြောင်းတည်း ဒေါင်လိုက်/အလျားလိုက် အလယ်ပို့ခြင်း */
    div[data-testid="stTable"] th,
    div[data-testid="stTable"] th * {
        text-align: center !important;
        vertical-align: middle !important;
        white-space: nowrap !important; /* စာလုံးလုံးဝ အောက်မဆင်းစေရန် */
        word-break: keep-all !important;
    }
    
    div[data-testid="stTable"] th {
        background-color: #f0f2f6 !important;
        padding: 12px 20px !important;
    }
    
    /* ၄။ Cells (ဒေတာများ) ကို တစ်ကြောင်းတည်း ဒေါင်လိုက်/အလျားလိုက် အလယ်ပို့ခြင်း */
    div[data-testid="stTable"] td,
    div[data-testid="stTable"] td * {
        text-align: center !important;
        vertical-align: middle !important;
        white-space: nowrap !important; /* နာမည်ရှည်များပါ လုံးဝတစ်ကြောင်းတည်း ဖြစ်စေရန် */
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

# Tab နာမည်များ သတ်မှတ်ခြင်း
USAGE_TAB_NAME = "EngUsageTracker"  # မူရင်းသုံးစွဲမှုစာရင်း Tab
OUT_TAB_NAME = "Out Of PM"          # ဒုတိယပစ္စည်းထုတ်ယူသွားသည့် Tab

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
            df_out['Date'] = pd.to_datetime(df_out['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
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

    # ၁။ ကော်လံများ စစ်ထုတ်ခြင်းနှင့် ခေါင်းစဉ်များကို အတိုကောက်ပြောင်းလဲခြင်း
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

    # ၂။ Dropdown ရွေးချယ်မှုအပိုင်း (2-Column)
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

    # ၃။ Filter Logic
    result_df = filtered_df.copy()
    
    if selected_engineer != "All Engineers":
        result_df = result_df[result_df['Engineer Name'] == selected_engineer]
        
    if selected_date != "All Dates":
        result_df = result_df[result_df['Date'] == selected_date]

    st.divider()

    # ၄။ ရလဒ်အား Table ဖြင့် ပြသခြင်း
    if not result_df.empty:
        st.markdown("<h3 style
