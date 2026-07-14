import streamlit as st
import pandas as pd

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်သော အခင်းအကျင်း)
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🎨 ဇယားကို Screen အတင်းမညှစ်ဘဲ စာလုံးအရှည်အတိုင်း တစ်ကြောင်းတည်း (Center) ပို့ပေးမည့် CSS အသစ်
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

# App Header (HTML သုံး၍ အလယ်သို့ ပို့ထားပါသည်)
st.markdown("<h1 style='text-align: center;'>📱 Engineer Accessories Tracker</h1>", unsafe_allow_html=True)

# ⚠️ သင်၏ Google Sheet CSV Link အမှန်ကို အောက်ကနေရာတွင် ထည့်ပါ
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=30) # Data update မြန်စေရန် စက္ကန့် ၃၀ သတ်မှတ်
def load_data():
    df = pd.read_csv(GSHEET_CSV_URL)
    # Date Column ကို စာသားမှ နေ့စွဲ Format သို့ ပြောင်းလဲခြင်း
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    return df

# ဒေတာဆွဲယူခြင်းကို သီးသန့် try-except ဖြင့် ဖမ်းယူခြင်း
df = None
try:
    df = load_data()
except Exception as e:
    st.error(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")

# ဒေတာ အောင်မြင်စွာ ရရှိမှသာ အောက်ပါ UI ပိုင်းများကို လုပ်ဆောင်မည်
if df is not None:
    
    # 🔍 Google Sheet ထဲတွင် Sleeve / Sleeves Column နာမည်ကို ရှာဖွေခြင်း
    sleeve_col_in_sheet = None
    possible_sleeve_names = [
        'Sleeves with 2 steels', 
        'Sleeve with 2 Steels', 
        'Sleeves with 2 Steels', 
        'Sleeve with 2 steels'
    ]
    
    for col in df.columns:
        if col.strip() in possible_sleeve_names:
            sleeve_col_in_sheet = col
            break
            
    if not sleeve_col_
