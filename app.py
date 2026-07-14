import streamlit as st
import pandas as pd

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်သော အခင်းအကျင်း)
st.set_page_config(page_title="Accessories Tracker", layout="centered")

# 📱 ခေါင်းစဉ်ကို အလယ်တည့်တည့်သို့ ပို့ခြင်း (Streamlit's Built-in style)
st.markdown("<h1 style='text-align: center;'>📱 Engineer Accessories Tracker</h1>", unsafe_allowed_html=True)

# ⚠️ သင်၏ Google Sheet CSV Link အမှန်ကို အောက်ပါနေရာတွင် ထည့်ပါ
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Gzy3wOg-Ug_PdvxLKzR5Et1-vs6huzaP4lQjioQouKc/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=30) # ဒေတာ update မြန်စေရန် စက္ကန့် ၃၀ သတ်မှတ်
def load_data():
    df = pd.read_csv(GSHEET_CSV_URL)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    return df

try:
    df = load_data()
    
    # ပြသချင်သော Column များအား Map လုပ်ခြင်း (Township & Car-ID ကို ဖယ်ပြီး TKT/POI/CPE ထည့်ထားသည်)
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
    
    available_cols = [col for col in columns_mapping.keys() if col in df.columns]
    filtered_df = df[available_cols].copy()
    filtered_df = filtered_df.rename(columns={c: columns_mapping[c] for c in available_cols})

    # Dropdowns (Engineer & Date)
    col1, col2 = st.columns(2)
    with col1:
        engineers_list = sorted(filtered_df['Engineer Name'].dropna().unique())
        selected_engineer = st.selectbox("👷 Engineer Name:", options=["All Engineers"] + list(engineers_list))
    with col2:
        dates_list = sorted(filtered_df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("📅 Date:", options=["All Dates"] + list(dates_list))

    # Filter ပိုင်း
    result_df = filtered_df.copy()
    if selected_engineer != "All Engineers":
        result_df = result_df[result_df['Engineer Name'] == selected_engineer]
    if selected_date != "All Dates":
        result_df = result_df[result_df['Date'] == selected_date]

    st.divider()

    if not result_df.empty:
        # Table ခေါင်းစဉ်များကို အလယ်တည့်တည့် ပို့ခြင်း
        st.markdown("<h3 style='text-align: center;'>📊 ကြည့်ရှုနေသော မှတ်တမ်းဇယား</h3>", unsafe_allowed_html=True)
        st.dataframe(result_df, use_container_width=True, hide_index=True)
        
        st.markdown("<h3 style='text-align: center;'>📈 Total Used Summary</h3>", unsafe_allowed_html=True)
        numeric_cols = result_df.select_dtypes(include='number').columns
        
        if not numeric_cols.empty:
            summary_list = []
            for col in numeric_cols:
                total_val = result_df[col].sum()
                if total_val % 1 == 0:
                    formatted_val = f"{int(total_val)}"
                else:
                    formatted_val = f"{total_val:.1f}"
                summary_list.append({'ပစ္စည်းအမျိုးအမည်': col, 'စုစုပေါင်းအရေအတွက်': formatted_val})
                
            summary_table = pd.DataFrame(summary_list)
            st.dataframe(summary_table, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ ရွေးချယ်ထားသော ဒေတာ မရှိသေးပါ။")

except Exception as e:
    st.error(f"❌ Error: {e}")
