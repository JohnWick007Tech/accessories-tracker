import streamlit as st
import pandas as pd

# Page Configuration (ဖုန်းအတွက် ပိုမိုသေသပ်သော အခင်းအကျင်း)
st.set_page_config(
    page_title="Accessories Tracker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🎨 ဇယားထဲက စာသားများကို လုံးဝအောက်ကြောင်းမဆင်းစေဘဲ (No Wrap) တစ်ကြောင်းတည်း အလယ်တည့်တည့်ကျစေမည့် CSS အသစ်
st.html("""
<style>
    /* ဇယားခေါင်းစဉ် (Headers) များကို လုံးဝ စာကြောင်းမခွဲဘဲ တစ်ကြောင်းတည်း အလယ်ပို့ရန် */
    th, [data-testid="stTableHeader"] div {
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        white-space: nowrap !important; /* စာကြောင်းအောက်မဆင်းစေရန် */
        word-break: keep-all !important;
    }
    
    /* ဇယားထဲက ဒေတာ Cell တန်ဖိုးများကိုလည်း တစ်ကြောင်းတည်း အလယ်ပို့ရန် */
    td, [data-testid="styled-cell"] div {
        text-align: center !important;
        white-space: nowrap !important; /* Date နှင့် Name များ လုံးဝတစ်ကြောင်းတည်းပေါ်စေရန် */
        word-break: keep-all !important;
    }
    
    /* စုစုပေါင်းဇယားကွက် သပ်ရပ်စေရန် */
    div[data-testid="stTable"] td {
        text-align: center !important;
        white-space: nowrap !important;
    }
</style>
""")

# App Header
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
            
    if not sleeve_col_in_sheet:
        for col in df.columns:
            if 'sleeve' in col.lower() and '2' in col:
                sleeve_col_in_sheet = col
                break
                
    if not sleeve_col_in_sheet:
        sleeve_col_in_sheet = 'Sleeve with 2 Steels'

    # ၁။ ကော်လံများ စစ်ထုတ်ခြင်းနှင့် ခေါင်းစဉ်များကို အတိုကောက်ပြောင်းလဲခြင်း
    # (ဖုန်းစခရင်အကျယ်နှင့် ကိုက်ညီစေရန် ခေါင်းစဉ်အတိုများကို သုံးထားပါသည်)
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
    
    # Column နာမည်များကို အစားထိုးခြင်း
    filtered_df = filtered_df.rename(columns={col: columns_mapping[col] for col in available_cols})

    # ၂။ Dropdown ရွေးချယ်မှုအပိုင်း (2-Column ဖြင့် စနစ်တကျခွဲထားခြင်း)
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
        
        # ကော်လံအလိုက် တန်ဖိုးများနှင့် စာသားများကို အလယ် (Center) ရောက်စေရန်
        custom_align_config = {}
        for col in result_df.columns:
            if pd.api.types.is_numeric_dtype(result_df[col]):
                custom_align_config[col] = st.column_config.NumberColumn(alignment="center")
            else:
                custom_align_config[col] = st.column_config.TextColumn(alignment="center")
        
        # ⚠️ st.dataframe ကို သုံးပြီး layout ကောင်းမွန်အောင် ပြန်လည်ပြသခြင်း
        st.dataframe(
            result_df, 
            use_container_width=True, 
            hide_index=True,
            column_config=custom_align_config
        )
        
        # ၅။ စုစုပေါင်းအရေအတွက် တွက်ချက်မှုအပိုင်း
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
                    
                summary_list.append({'Accessories': col, 'Total Usage': formatted_val})
            
            summary_table = pd.DataFrame(summary_list)
            
            # စုစုပေါင်းပြသမည့် ဇယားမှ တန်ဖိုးများကို အလယ် (Center) သို့ ပို့ခြင်း
            summary_align_config = {
                'Accessories': st.column_config.TextColumn(alignment="center"),
                'Total Usage': st.column_config.TextColumn(alignment="center")
            }
            
            st.dataframe(
                summary_table,
                use_container_width=True,
                hide_index=True,
                column_config=summary_align_config
            )
            
    else:
        st.warning("⚠️ ရွေးချယ်ထားသော အချက်အလက်များနှင့် ကိုက်ညီသည့် မှတ်တမ်း မရှိသေးပါ။")
