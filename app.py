import streamlit as st
import pandas as pd
import streamlit_analytics2 as streamlit_analytics  # 👈 Analytics tracker ကို Import လုပ်ခြင်း

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်သော အခင်းအကျင်း)
# (၎င်းသည် အမြဲတမ်း ပထမဆုံး Streamlit command ဖြစ်ရပါမည်)
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 📊 ဝင်ရောက်ကြည့်ရှုသူများကို စတင်ခြေရာခံခြင်း
# (အောက်ပါ ကုဒ်များအားလုံးကို ၎င်းအောက်တွင် Indent လုပ်ပြီး ထည့်သွင်းထားပါသည်)
with streamlit_analytics.track():

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
    st.markdown("<h3 style='text-align: center;'>📱 Eng Usage Checker</h3>", unsafe_allow_html=True)

    # ⚠️ သင်၏ Google Sheet CSV Link အမှန်ကို အောက်ကနေရာတွင် ထည့်ပါ
    GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc/gviz/tq?tqx=out:
