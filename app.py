import streamlit as st
import pandas as pd

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်သော အခင်းအကျင်း)
st.set_page_config(page_title="Accessories Tracker", layout="centered")

st.title("📱 Engineer Accessories Tracker")

# ⚠️ သင်၏ Google Sheet CSV Link အမှန်ကို အောက်ကနေရာတွင် ထည့်ပါ
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=30) # Data update မြန်စေရန် စက္ကန့် ၃၀ သတ်မှတ်
def load_data():
    df = pd.read_csv(GSHEET_CSV_URL)
    
    # Date Column ကို စာသားမှ နေ့စွဲ Format သို့ ပြောင်းလဲခြင်း
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    return df

try:
    df = load_data()
    
    # ၁။ လိုချင်သော ကော်လံများ စစ်ထုတ်ခြင်း (C နှင့် F Column များဖြစ်သော Township နှင့် Car-ID အပါအဝင်)
    columns_mapping = {
        'Date': 'Date',
        'Township': 'Township',                  # Google Sheet C Column
        'Engineer Car-ID': 'Car-ID',            # Google Sheet F Column
        'Engineer Name': 'Engineer Name',
        'Patch Cords(SC/APC) 1M': 'Patch Cords\n(1M)',          # Title ကို ၂ ဆင့်ခွဲရန် \n သုံးထားပါသည်
        'Patch Cords(SC/APC) 1.5M': 'Patch Cords\n(1.5M)',
        'One Core OTB Box': 'One Core\nOTB Box',
        'Sleeve': 'Sleeve',
        'Customize (Pencil Kit , white)': 'Customize\n(Pencil Kit)',
        'Standard (Pencil Kit , white)': 'Standard\n(Pencil Kit)'
    }
    
    # လက်ရှိ Sheet ထဲမှာ ရှိနေတဲ့ column တွေကိုပဲ ယူမည်
    available_cols = [col for col in columns_mapping.keys() if col in df.columns]
    filtered_df = df[available_cols].copy()
    
    # Column နာမည်များကို ဖုန်းတွင် ကြည့်ရကျဉ်းအောင် အတိုကောက်နှင့် ၂ ဆင့်ပုံစံ ပြောင်းခြင်း
    filtered_df = filtered_df.rename(columns={col: columns_mapping[col] for col in available_cols})

    # ၂။ Dropdown ရွေးချယ်မှုအပိုင်း (Engineer Name ကော Date ပါ ရွေးချယ်နိုင်ရန်)
    col1, col2 = st.columns(2)
    
    with col1:
        engineers_list = sorted(filtered_df['Engineer Name'].dropna().unique())
        selected_engineer = st.selectbox(
            "👷 Engineer Name:",
            options=["All Engineers"] + list(engineers_list)
        )
        
    with col2:
        # နေ့စွဲများကို နောက်ဆုံးရက်က အပေါ်ဆုံးကပြရန် အစဉ်လိုက်စီခြင်း
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

    # ၄။ ရလဒ်အား Table ဖြင့် ပြသခြင်း
    if not result_df.empty:
        st.subheader("📊 ကြည့်ရှုနေသော မှတ်တမ်းဇယား")
        
        # ဖုန်းမျက်နှာပြင်တွင် စာသားများ အလယ်ကွက်တိဖြစ်ပြီး ကျဉ်းကျဉ်းလင်းလင်း ဖြစ်စေရန် စတိုင်သွင်းခြင်း
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
            for col in numeric_cols:
                total_val = result_df[col].sum()
                
                # ဒဿမနောက်က 0 ဖြစ်နေလျှင် ကိန်းပြည့်ပဲပြရန်၊ မဟုတ်လျှင် ဒဿမ ၁ နေရာပဲပြရန်
                if total_val % 1 == 0:
                    formatted_val = f"{int(total_val)}"
                else:
                    formatted_val = f"{total_val:.1f}"
                    
                summary_list.append({'Accessories': col, 'Total': formatted_val})
            
            summary_table = pd.DataFrame(summary_list)
            st.table(summary_table)
            
    else:
        st.warning("⚠️ ရွေးချယ်ထားသော အချက်အလက်များနှင့် ကိုက်ညီသည့် မှတ်တမ်း မရှိသေးပါ။")

except Exception as e:
    st.error(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")
