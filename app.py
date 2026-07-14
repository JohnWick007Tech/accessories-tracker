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
            
    # ⚠️ ဒီနေရာမှာ error တက်နေတာဖြစ်လို့ အောက်ကစာကြောင်းတွေအတိုင်း အပြည့်အစုံ ပြန်ပြင်ပါ
    if not sleeve_col_in_sheet:
        for col in df.columns:
            if 'sleeve' in col.lower() and '2' in col:
                sleeve_col_in_sheet = col
                break
                
    if not sleeve_col_in_sheet:
        sleeve_col_in_sheet = 'Sleeve with 2 Steels'
