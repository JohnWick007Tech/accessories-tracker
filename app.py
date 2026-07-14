import streamlit as st
import pandas as pd

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်ပြီး ရှင်းလင်းသော အခင်းအကျင်း)
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# App Header ပိုင်း
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
    
    # ၁။ ကော်လံများ စစ်ထုတ်ခြင်းနှင့် ခေါင်းစဉ်များကို အတိုကောက်/နှစ်ဆင့်ပြောင်းလဲခြင်း
    columns_mapping = {
        'Date': 'Date',
        'Engineer Name': 'Engineer Name',
        'TKT/POI/CPE': 'TKT/POI/CPE',                         
        'Patch Cords(SC/APC) 1M': 'Patch Cords (1M)',          
        'Patch Cords(SC/APC) 1.5M': 'Patch Cords (1.5M)',
        'One Core OTB Box': 'One Core OTB Box',
        'Sleeve': 'Sleeve',
        'Customize (Pencil Kit , white)': 'Customize (Pencil Kit)',
        'Standard (Pencil Kit , white)': 'Standard (Pencil Kit)'
    }
    
    # လက်ရှိ Sheet ထဲမှာ ရှိနေတဲ့ column တွေကိုပဲ ယူမည်
    available_cols = [col for col in columns_mapping.keys() if col in df.columns]
    filtered_df = df[available_cols].copy()
    
    # Column နာမည်များကို သတ်မှတ်ချက်အတိုင်း အစားထိုးခြင်း
    filtered_df = filtered_df.rename(columns={col: columns_mapping[col] for col in available_cols})

    # ၂။ Dropdown ရွေးချယ်မှုအပိုင်း (အလယ်တည့်တည့်ကျအောင် 2-Column ဖြင့် စနစ်တကျခွဲထားခြင်း)
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
        
        # ⚠️ ကိန်းဂဏန်း 0, 1 များ၊ Date များနှင့် အချက်အလက်အားလုံးကို ဇယားအလယ်တည့်တည့် (Center alignment) ရောက်အောင် သတ်မှတ်ခြင်း
        center_align_config = {
            col: st.column_config.Column(alignment="center") 
            for col in result_df.columns
        }
        
        st.dataframe(
            result_df, 
            use_container_width=True, 
            hide_index=True,
            column_config=center_align_config # Column အားလုံးကို Center ပို့ရန်
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
                    
                summary_list.append({'ပစ္စည်းအမျိုးအမည်': col, 'စုစုပေါင်းအရေအတွက်': formatted_val})
            
            summary_table = pd.DataFrame(summary_list)
            
            # စုစုပေါင်းပြသမည့် ဇယားကော်လံများကိုလည်း အလယ်ဗဟို (Center) သို့ စနစ်တကျ ပို့ခြင်း
            summary_config = {
                'ပစ္စည်းအမျိုးအမည်': st.column_config.Column(alignment="center"),
                'စုစုပေါင်းအရေအတွက်': st.column_config.Column(alignment="center")
            }
            
            st.dataframe(
                summary_table,
                use_container_width=True,
                hide_index=True,
                column_config=summary_config # စုစုပေါင်းဇယားကိုပါ Center ပို့ရန်
            )
            
    else:
        st.warning("⚠️ ရွေးချယ်ထားသော အချက်အလက်များနှင့် ကိုက်ညီသည့် မှတ်တမ်း မရှိသေးပါ။")

except Exception as e:
    st.error(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {e}")
