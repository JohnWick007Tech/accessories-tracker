import streamlit as st
import pandas as pd

# Page Configuration (ဖုန်းအတွက် အလယ်တည့်တည့်ကျအောင် ပြင်ဆင်ခြင်း)
st.set_page_config(page_title="Accessories Tracker", layout="centered")

# CSS သုံးပြီး စာသားအားလုံးနှင့် Element အားလုံးကို Center (အလယ်တည့်တည့်) ပို့ပေးခြင်း
st.markdown("""
    <style>
    /* ခေါင်းစဉ်များနှင့် စာသားများကို အလယ်ပို့ရန် */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stMarkdown {
        text-align: center !important;
    }
    
    /* Dropdown ခေါင်းစဉ်များကို အလယ်ပို့ရန် */
    div[data-testid="stWidgetLabel"] {
        text-align: center !important;
        width: 100%;
    }
    
    /* Table ထဲက Data များကို အလယ်တည့်တည့် ထားရန် */
    div[data-testid="stTable"] table {
        margin-left: auto;
        margin-right: auto;
        text-align: center !important;
    }
    th, td {
        text-align: center !important;
    }
    </style>
""", unsafe_allowed_html=True)

# အလယ်တည့်တည့်တွင် ပေါ်မည့် App ခေါင်းစဉ်
st.title("📱 Engineer Accessories Tracker")

# ⚠️ သင်၏ Google Sheet CSV Link အမှန်ကို အောက်ကနေရာတွင် ထည့်ပါ
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=30) # ဒေတာ update မြန်စေရန် စက္ကန့် ၃၀ သတ်မှတ်
def load_data():
    df = pd.read_csv(GSHEET_CSV_URL)
    
    # Date Column ကို စာသားမှ နေ့စွဲ Format သို့ ပြောင်းလဲခြင်း
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    return df

# ဒေတာ ဆွဲယူခြင်းအား try-except ဖြင့် ဖမ်းယူခြင်း
try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ Google Sheet ဒေတာ ချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")
    data_loaded = False

# ဒေတာ အောင်မြင်စွာ ရရှိမှသာ အောက်ပါ အလုပ်များကို ဆက်လုပ်မည်
if data_loaded:
    # ၁။ ကော်လံအသစ်များနှင့် နာမည်များကို ပြောင်းလဲခြင်း
    columns_mapping = {
        'Date': 'Date',
        'Engineer Name': 'Engineer Name',
        'TKT/POI/CPE': 'TKT/POI/CPE',                         
        'Patch Cords(SC/APC) 1M': 'Patch Cords\n(1M)',          
        'Patch Cords(SC/APC) 1.5M': 'Patch Cords\n(1.5M)',
        'One Core OTB Box': 'One Core\nOTB Box',
        'Sleeve': 'Sleeve',
        'Customize (Pencil Kit , white)': 'Customize\n(Pencil Kit)',
        'Standard (Pencil Kit , white)': 'Standard\n(Pencil Kit)'
    }
    
    # Sheet ထဲရှိသော column များကိုပဲ ယူမည်
    available_cols = [col for col in columns_mapping.keys() if col in df.columns]
    filtered_df = df[available_cols].copy()
    
    # Column နာမည်များကို ဖုန်းတွင် ကြည့်ရကျဉ်းအောင် အတိုကောက်ပြောင်းခြင်း
    filtered_df = filtered_df.rename(columns={col: columns_mapping[col] for col in available_cols})

    # ၂။ Dropdown ရွေးချယ်မှုအပိုင်း (အလယ်တည့်တည့်တွင် စီရန်)
    col1, col2 = st.columns(2)
    
    with col1:
        engineers_list = sorted(filtered_df['Engineer Name'].dropna().unique())
        selected_engineer = st.selectbox(
            "👷 Engineer Name:",
            options=["All Engineers"] + list(engineers_list)
        )
        
    with col2:
        dates_list = sorted(filtered_df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox(
            "📅 Date:",
            options=["All Dates"] + list(dates_list)
        )

    # ၃။ Filter Logic (ရွေးချယ်မှုအပေါ်မူတည်ပြီး စစ်ထုတ်ခြင်း)
    result_df = filtered_df.copy()
    
    if selected_engineer != "All Engineers":
        result_df = result_df[result_df['Engineer Name'] == selected_engineer]
        
    if selected_date != "All Dates":
        result_df = result_df[result_df['Date'] == selected_date]

    st.divider()

    # ၄။ ရလဒ်အား ဇယား (Table) ဖြင့် ပြသခြင်း
    if not result_df.empty:
        st.subheader("📊 ကြည့်ရှုနေသော မှတ်တမ်းဇယား")
        
        # ဇယားအား ဖုန်း Screen အပြည့် အလယ်တည့်တည့် ပုံစံဖြင့် ပြသခြင်း
        st.dataframe(
            result_df, 
            use_container_width=True, 
            hide_index=True
        )
        
        # ၅။ စုစုပေါင်းအရေအတွက် တွက်ချက်မှုအပိုင်း (ဒဿမ ရှင်းလင်းရေး အပါအဝင်)
        st.subheader("📈 Total Used Summary")
        
        # ကိန်းဂဏန်း Column များကိုသာ စုစုပေါင်းတွက်မည်
        numeric_cols = result_df.select_dtypes(include='number').columns
        
        if not numeric_cols.empty:
            summary_list = []
            for col in numeric
