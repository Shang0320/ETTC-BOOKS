import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

# 設定頁面標題和版面，採用深色主題
st.set_page_config(page_title="教測中心圖書查詢系統", layout="wide")

# 利用 st.columns 將 LOGO 與標題並排
col1, col2 = st.columns([1,4])
with col1:
    # 請確認圖片權限為公開，這裡使用一個示意圖片網址
    st.image("https://th.bing.com/th/id/OIP.9jKbLb2tJQxAcb_7avTrdAHaHa?rs=1", width=120)
with col2:
    st.markdown("<h1 style='color:#FFEB3B;'>海巡署教育訓練測考中心圖書查詢系統</h1>", unsafe_allow_html=True)

# 定義函數從 Google Sheets 讀取資料
@st.cache_data(ttl=600)  # 快取 10 分鐘
def load_data():
    try:
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )
        client = gspread.authorize(credentials)
        # 直接硬編碼 Google Sheets URL
        spreadsheet_url = "https://github.com/Shang0320/ETTC-BOOKS/blob/5fc5be38bc2139df7395a027679bd45248ba4b8f/ettclogo.png?raw=true"
        sheet = client.open_by_url(spreadsheet_url).worksheet("Sheet1")
        df = get_as_dataframe(sheet, evaluate_formulas=True, skiprows=0)
        df = df.dropna(how='all')
        if '畢業年度' in df.columns:
            df['畢業年度'] = pd.to_numeric(df['畢業年度'], errors='coerce')
        if '論文出版年' in df.columns:
            df['論文出版年'] = pd.to_numeric(df['論文出版年'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"讀取數據時發生錯誤: {e}")
        return pd.DataFrame()

# 載入資料
with st.spinner("正在從 Google Drive 讀取資料..."):
    df = load_data()

# 自定義 CSS，呈現高對比度、華麗的介面
st.markdown("""
    <style>
    /* 整體背景與文字 */
    body {
        background-color: #121212;
        color: #E0E0E0;
    }
    .stButton>button {
        background-color: #FF5722;
        color: #FFFFFF;
        border: none;
        padding: 0.5em 1em;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #E64A19;
    }
    /* 標題 */
    h1, h2, h3 {
        color: #FFEB3B;
    }
    /* 資料表 */
    .css-1oe6wy3 {
        background-color: #1E1E1E !important;
    }
    table {
        background-color: #1E1E1E;
        border: 1px solid #424242;
    }
    th {
        background-color: #FF9800;
        color: #000000;
        font-weight: bold;
    }
    td {
        border: 1px solid #424242;
    }
    tr:nth-child(even) {
        background-color: #2C2C2C;
    }
    tr:hover {
        background-color: #424242;
    }
    /* 搜尋區塊 */
    .stTextInput>div>div>input {
        background-color: #1E1E1E;
        color: #E0E0E0;
        border: 1px solid #424242;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

if df.empty:
    st.error("無法獲取資料，請檢查連接和權限設定。")
else:
    st.success(f"已成功讀取 {len(df)} 筆資料")
    
    st.header("搜尋功能")
    
    # 單一查詢方式
    search_method = st.radio("選擇搜尋方式:", ["論文名稱", "研究生", "指導教授"])
    
    if search_method == "論文名稱":
        search_input = st.text_input("輸入論文名稱關鍵字:")
        if search_input:
            filtered_df = df[df["論文名稱"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
    elif search_method == "研究生":
        search_input = st.text_input("輸入研究生姓名關鍵字:")
        if search_input:
            filtered_df = df[df["研究生"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
    else:  # 指導教授
        search_input = st.text_input("輸入指導教授姓名關鍵字:")
        if search_input:
            filtered_df = df[df["指導教授"].str.contains(search_input, case=False, na=False)]
            st.write(f"搜尋結果: {len(filtered_df)} 筆")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("沒有符合的搜尋結果")
    
    # 進階篩選，預設展開
    with st.expander("進階篩選", expanded=True):
        df_filtered = df.copy()
        col1, col2 = st.columns(2)
        with col1:
            if "校院名稱" in df.columns:
                schools = sorted(df["校院名稱"].dropna().unique().tolist())
                selected_schools = st.multiselect("選擇校院名稱:", schools)
                if selected_schools:
                    df_filtered = df_filtered[df_filtered["校院名稱"].isin(selected_schools)]
            if "系所名稱" in df.columns:
                departments = sorted(df["系所名稱"].dropna().unique().tolist())
                selected_departments = st.multiselect("選擇系所名稱:", departments)
                if selected_departments:
                    df_filtered = df_filtered[df_filtered["系所名稱"].isin(selected_departments)]
        with col2:
            if "學位類別" in df.columns:
                degrees = sorted(df["學位類別"].dropna().unique().tolist())
                selected_degrees = st.multiselect("選擇學位類別:", degrees)
                if selected_degrees:
                    df_filtered = df_filtered[df_filtered["學位類別"].isin(selected_degrees)]
            if "論文出版年" in df.columns:
                min_year = int(df["論文出版年"].min())
                max_year = int(df["論文出版年"].max())
                year_range = st.slider("論文出版年範圍:", min_year, max_year, (min_year, max_year))
                df_filtered = df_filtered[(df_filtered["論文出版年"] >= year_range[0]) & (df_filtered["論文出版年"] <= year_range[1])]
        
        st.write(f"進階篩選後，共有 {len(df_filtered)} 筆論文")
        st.dataframe(df_filtered)
    
    # 資料概覽與統計圖表
    if st.checkbox("顯示資料概覽"):
        st.subheader("資料統計")
        if "系所名稱" in df.columns:
            dept_counts = df["系所名稱"].value_counts()
            st.bar_chart(dept_counts)
        if "論文出版年" in df.columns:
            year_counts = df["論文出版年"].value_counts().sort_index()
            st.line_chart(year_counts)
